@echo off

rem Set variables
set path_venv_script=%LOCALAPPDATA%\Building_urban_analysis\tool_venv\Scripts
set path_python_scripts=%LOCALAPPDATA%\Building_urban_analysis\Scripts

echo Activate the virtual environment
call "%path_venv_script%\activate.bat"

echo Run the solar radiation simulation
python "%path_python_scripts%\components_gh\get_id_buildings\main_get_id_buildings.py" -t 1 %* > "%LOCALAPPDATA%\Building_urban_analysis\Simulation_temp\out.txt" 2>&1

rem Deactivate the virtual environment
deactivate
pause