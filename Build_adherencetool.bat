@ECHO OFF
REM -----------------------------------------------------------------
REM Batch file to build GSC_test.exe
REM Prior to building ensure that needed requirements are installed
REM using pip install -r requirements.txt
REM take %1 - as the version 
REM build_adherence_tool.bat 1.0.0 
REM -----------------------------------------------------------------
ECHO Make adherence tool executable 
git describe --always --abbrev=6 --match= > tempVersion
set /p myVer= < tempVersion 

ECHO toolVersion ="%1-%myVer%"> tool_version.py
ECHO def getToolVersion(): >> tool_version.py
ECHO 	return toolVersion >> tool_version.py

rmdir /Q /S dist

rem python -m PyInstaller --clean ADT-Tool.spec 
python -m PyInstaller --onefile AdherenceTool.py


IF NOT EXIST dist\AdherenceTool.exe GOTO BUILDFAIL
echo copy files over
copy GSLogParser.exe dist\.
xcopy templates dist\templates /E /I /Y
python -m zipfile -c GSAdherence-%1.zip dist/

IF NOT EXIST GSAdherence-%1.zip GOTO BUILDFAIL
GOTO DONE
:BUILDFAIL
ECHO Errors building GSAdherence-%1.exe
:DONE