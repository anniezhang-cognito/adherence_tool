from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import win32api
import os
from datetime import datetime, timedelta
import shutil

VERSION='1.0.0'

fontType = 'Arial'
fontSize = 14

def setup_folder(subject_id, device_id):
    baseDir = "C:\Cognitotx"
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    root_dir = os.path.join(baseDir,  subject_id + "_" + device_id + "_" + datetime.now().strftime("%Y%m%d%H%M"))
    return root_dir

LogWriter = None
LogLines = []

def create_writer(logdir, version):
    global LogWriter
    global LogLines
    logdir = os.path.join(logdir, "logs")
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    dtstamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"AdherenceLog.csv"
    LogWriter = os.path.join(logdir, filename)
    print(f"Log File:{LogWriter}")
    writeLog(f"----------------------  Staring Adherence Tool {dtstamp}  ----------------------")
    writeLog('Adherence Tool Version', version)
    if len(LogLines) > 0:
        print(LogLines)
        for line in LogLines:
            # log to the file if it exists
            fp = open(LogWriter, "a+")
            fp.write(line)
            fp.close()
        LogLines = []

def writeLog(message='', detail='', component='Adherence-Tool'):
    global LogLines
    datestr = datetime.isoformat(datetime.now())
    try:
        output_str = f"{datestr},{component},{message},{detail}\n"
        if LogWriter is None:
            LogLines.append(output_str)
        else:
            # log to the file if it exists
            fp = open(LogWriter, "a+")
            fp.write(output_str)
            fp.close()
    except Exception as ex:
        print(f"Error writing to file Ex:{ex}")


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Adherence Tool")
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
        self.logParser_button = tk.Button(self, text="Get Adherence", command=self.execLogParser, font=(fontType, fontSize), bg='green', fg='white', height=2, width=30)
        self.logParser_button.place(relx = 0.15, rely = 0.55)

    def execLogParser(self):
        writeLog("INFO", "Starting processing")

        progress_string = "Starting processing"
        self.logParser_button['text'] = progress_string
        self.logParser_button.update()

        subjectID = self.subjectIDentry.get()
        print(subjectID)
        deviceID = self.deviceIDentry.get()
        print(deviceID)

        zipcode = self.zipcodeEntry.get()

        gs120drive = self.get_gs120_drive()
        
        if gs120drive is None:
            writeLog("ERROR", "Connect GS120 and start again")
            messagebox.showerror("Error", "Connected GS120 in TAR mode not found.  Please connect and try again.")
            progress_string = "Get Adherence"
            self.logParser_button['text'] = progress_string
            self.logParser_button.update()
            return
        else:
            writeLog("INFO", f"GS120 Drive {gs120drive}")
            print(f"GS120 drive {gs120drive}")
            base_dir = setup_folder(subjectID, deviceID)
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            create_writer(base_dir, VERSION)
            device_dir = os.path.join(base_dir, "deviceData")
            writeLog("INFO", f"Copying GS Files")
            inputdir = self.copy_log_files(gs120drive, device_dir)

        print("run log parser")
        writeLog("INFO", f"Running Parser")
        progress_string = "Running Parser"
        self.logParser_button['text'] = progress_string
        self.logParser_button.update()
        output_dir = os.path.join(base_dir, "Parser")
        logArguments = "--input " + inputdir + " --output " + output_dir + " --subject " + subjectID + " --device " + deviceID +  " --zipcode " + zipcode
        print(logArguments)
        if not os.path.exists("GSLogParser.exe"):
            writeLog("ERROR", f"GSLogParser.exe not installed.")
            messagebox.showerror("Error", "GSLogParser.exe not installed.")
            progress_string = "Get Adherence"
            self.logParser_button['text'] = progress_string
            self.logParser_button.update()
            return

        exec_result = os.system("GSLogParser.exe " + logArguments)
        if exec_result > 0:
            writeLog("ERROR", f"Error Running Parser - check logs")
            messagebox.showerror("Error", "LogParser.exe had errors.")
            progress_string = "Get Adherence"
            self.logParser_button['text'] = progress_string
            self.logParser_button.update()
            return

        reportFolder = os.path.join(base_dir, "Report" )
        if not os.path.exists(reportFolder):
            os.makedirs(reportFolder)

        tempReportFolder = os.path.join(output_dir, "Report" )
        src_file = os.listdir(tempReportFolder)
        if len(src_file) == 0:
            writeLog("ERROR", f"Can not generate adherence report! Please check subject ID and device ID.")
            messagebox.showerror("Error", "Can not generate adherence report! Please check subject ID and device ID.")
            return
        else:
            print(src_file)
            dst_file = os.path.join(reportFolder, f'AdherenceReport_{subjectID}_{deviceID}.pdf')
            writeLog("INFO", f"Copying {src_file} to {dst_file}.")
            shutil.copy(os.path.join(tempReportFolder, src_file[0]),  dst_file)
        #shutil.copy(summary_data['PDF File'], os.path.join(reportFolder, baseFileName))
            os.startfile(dst_file)

        writeLog("INFO", f"Done Parsing Adherence Data.")
        progress_string = "Done"
        self.logParser_button['text'] = progress_string
        self.logParser_button.update()

    def get_gs120_drive(self):
        return_drive = None
        progress_string = "Checking for GS120"
        self.logParser_button['text'] = progress_string
        self.logParser_button.update_idletasks()
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

        if return_drive is None:
            progress_string = "Get Adherence"
            self.logParser_button['text'] = progress_string
            self.logParser_button.update_idletasks()


        return return_drive

    def copy_log_files(self, source_dir, dest_dir):
        log_dir = os.path.join(dest_dir, "LOG")
        # Create the directory if it doesn't exist
        writeLog("INFO", f"Starting Copying GS Files", "copy_log_files")
        os.makedirs(log_dir, exist_ok=True)
        # Copy the log files to the structured directory
        for log_file in ["UPDATE.LOG", "PARTICLE.LOG", "ERROR.LOG"]:
            writeLog("INFO", f"Copying {log_file} Files", "copy_log_files")
            progress_string = "Copying {0} ({1}%)".format(log_file, 0)
            self.logParser_button['text'] = progress_string
            self.logParser_button.update()
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
                        self.logParser_button['text'] = progress_string
                        self.logParser_button.update()
                        self.after(20)

        return log_dir

    def open_file_dialog(self):
        file_path = filedialog.askdirectory(title="Select a Path")
        #if file_path:
        #    selected_file_label.config(text=f"Selected File: {file_path}")
        #    process_file(file_path)

if __name__ == "__main__":
    writeLog("Starting Adherence Tool")
    app = MainApplication()
    app.mainloop()

