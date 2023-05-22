@echo off

rem Set variables
set path_venv_script=%LOCALAPPDATA%\Building_urban_analysis\tool_venv\Scripts
set path_python_scripts=%LOCALAPPDATA%\Building_urban_analysis\Scripts

echo Activate the virtual environment
call "%path_venv_script%\activate.bat"

echo Run the main file, need to modify the path of the output file, it can only to Simulation_temp folder
python "%path_python_scripts%\mains_tool\start_BUA.py" %* > "%LOCALAPPDATA%\Building_urban_analysis\Simulation_temp\out.txt" 2>&1

rem Deactivate the virtual environment
deactivate
pause