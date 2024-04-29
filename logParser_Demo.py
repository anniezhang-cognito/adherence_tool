from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import win32api
import os
from datetime import datetime, timedelta
import shutil

fontType = 'Arial'
fontSize = 14

def setup_folder(subject_id, device_id):
    baseDir = "C:\Cognitotx"
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    root_dir = os.path.join(baseDir,  subject_id + "_" + device_id + "_" + datetime.now().strftime("%Y%m%d%H%M"))
    return root_dir

    
def get_gs120_drive():
    return_drive = None
    all_drives = win32api.GetLogicalDriveStrings()
    all_drives = all_drives.split('\000')[:-1]
    for drive in all_drives:
        print(f"Trying drive {drive}")
        label, fs, serial, c, d = win32api.GetVolumeInformation(drive)
        print(f"Label for {drive} is {label}")
        if label == 'GS120':
            try:
                # Check if the LOG directory exists in the new drive
                if "LOG" in os.listdir(drive):
                    return_drive = drive  # Return the drive letter of the GS120
                    break
            except Exception as e:
                print(f"Error accessing drive {drive}: {e}")

    return return_drive

def copy_log_files(source_dir, dest_dir):
    log_dir = os.path.join(dest_dir, "LOG")
    # Create the directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    # Copy the log files to the structured directory
    for log_file in ["UPDATE.LOG", "PARTICLE.LOG", "ERROR.LOG"]:
        src_file = f"{source_dir}/LOG/{log_file}"
        src_file_size = os.stat(src_file).st_size
        dst_file = f"{log_dir}/{log_file}"
        print("Copy data file " + log_file + " to "  + log_dir)
        # open the source file
        bytes_copied = 0
        with open(src_file, 'rb') as fsrc:
            with open(dst_file, 'wb') as fdst:
                # copy the file
                while True:
                    buf = fsrc.read(1024*1024)
                    if not buf:
                        break
                    fdst.write(buf)
                    bytes_copied = bytes_copied + len(buf)
                    pct_complete = int(bytes_copied/src_file_size*100)
                    progress_string = "Copying {0} ({1}%)".format(log_file, pct_complete)
                    print(progress_string)

    return log_dir
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Demo Application")
        self.geometry("500x300")

        # Create a container frame to hold all other frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}  # Dictionary to hold all frames

        # Loop through a tuple of all the page classes
        for F in (MainFrame, NextFrame):
            page_name = F.__name__  # Get the class name as a string
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame  # Use the class name as a string as the key
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame('MainFrame')  # Display the start page

    def show_frame(self, page_name):
        # Use the class name as a string to get the frame
        frame = self.frames[page_name]
        frame.tkraise()

class NextFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Create a start button that when clicked will show the COMPortSelectionScreen
        start_button = tk.Button(self, text="Start", command=self.doStart, font=('Helvetica', 18), bg='blue', fg='white', height=2, width=15)
        start_button.pack(pady=20)

    def doStart(self):
        print("doStart pressed")

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #title
        title_label = ttk.Label(self, text = "Log Parser for GS120 Data", font = "Calibri 24 bold")
        title_label.place(relx = 0.1, rely = 0.1)

        #input field - subject id
        
        subject_label = ttk.Label(self, text = "Enter subject ID: ")

        subject_label.place(relx = 0.1, rely = 0.25)

        subjectID = tk.StringVar()
        self.subjectIDentry = ttk.Entry(self, textvariable = subjectID)
        self.subjectIDentry.place(relx = 0.35, rely = 0.25)

        #input field - device id
        
        device_label = ttk.Label(self, text = "Enter device ID: " )
        device_label.place(relx = 0.1, rely = 0.35)

        deviceID = tk.StringVar()
        self.deviceIDentry = ttk.Entry(self, textvariable = deviceID)
        self.deviceIDentry.place(relx = 0.35, rely = 0.35)

        #input field - zip code
        zipcode_label = ttk.Label(self, text = "Subject Zip Code: " )
        zipcode_label.place(relx = 0.1, rely = 0.45)

        zipcode = tk.StringVar()
        self.zipcodeEntry = ttk.Entry(self, textvariable = zipcode)
        self.zipcodeEntry.place(relx = 0.35, rely = 0.45)

        #button     #browse
        #open_button = tk.Button(self, text="Browse", command=self.open_file_dialog)
        #open_button.place(relx = 0.75, rely = 0.45)
        
        #button Run LogParser
        logParser_button = tk.Button(self, text="Get Adherence", command=self.execLogParser, font=(fontType, fontSize), bg='green', fg='white', height=2, width=30)
        logParser_button.place(relx = 0.15, rely = 0.55)

    def execLogParser(self):

        subjectID = self.subjectIDentry.get()
        print(subjectID)
        deviceID = self.deviceIDentry.get()
        print(deviceID)

        zipcode = self.zipcodeEntry.get()

        gs120drive = get_gs120_drive()

        
        
        if gs120drive is None:
            messagebox.showerror("Error", "Connected GS120 in TAR mode not found.  Please connect and try again.")
        else:
            print(f"GS120 drive {gs120drive}")
            base_dir = setup_folder(subjectID, deviceID)
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            device_dir = os.path.join(base_dir, "deviceData")
            inputdir = copy_log_files(gs120drive, device_dir)

        print("run log parser")
        output_dir = os.path.join(base_dir, "Parser")
        logArguments = "--input " + inputdir + " --output " + output_dir + " --subject " + subjectID + " --device " + deviceID +  " --zipcode " + zipcode
        print(logArguments)
        os.system("GSLogParser.exe " + logArguments)

        reportFolder = os.path.join(base_dir, "Report" )
        if not os.path.exists(reportFolder):
            os.makedirs(reportFolder)

        tempReportFolder = os.path.join(output_dir, "Report" )
        src_file = os.listdir(tempReportFolder)
        if len(src_file) == 0:
            messagebox.showerror("Error", "Can not generate adherence report! Please check subject ID and device ID.")
        else:
            print(src_file)
            dst_file = os.path.join(reportFolder, f'AdherenceReport_{subjectID}_{deviceID}.pdf')
            shutil.copy(os.path.join(tempReportFolder, src_file[0]),  dst_file)
        #shutil.copy(summary_data['PDF File'], os.path.join(reportFolder, baseFileName))
            os.startfile(dst_file)
        
    def open_file_dialog(self):
        file_path = filedialog.askdirectory(title="Select a Path")
        #if file_path:
        #    selected_file_label.config(text=f"Selected File: {file_path}")
        #    process_file(file_path)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

