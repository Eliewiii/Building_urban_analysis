"""
Simulation flow to run EnergyPlus simulation on a hbjson model
"""

from sys import path

# Add the desired path to sys.path
path.append('c:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts')

from util_functions.prepare_hb_model_for_ep_simulation import from_hbjson_to_idf
from paths_to_files import path_ep, path_simulation_parameter, \
    path_hbjson_file_twobuildingsfirst, path_hbjson_file_twobuildingssecond, path_hbjson_file_onebuildingonly, path_epw_file
from util_functions.simulaton_ep import run_idf_windows_modified
from subprocess import run as run_cmdline
import os
import shutil


def create_folders(file_paths, directory_path):

    fmu_folders = []
    idf_folders = []
    for file_path in file_paths:
        folder_name = os.path.splitext(os.path.basename(file_path))[0]
        folder_path = os.path.join(directory_path, folder_name)
        idf_creation_path = os.path.join(folder_path, 'idf_creation')
        fmu_creation_path = os.path.join(folder_path, 'fmu_creation')
        
        if not os.path.exists(idf_creation_path):
            os.makedirs(idf_creation_path)
            idf_folders.append(idf_creation_path)

        if not os.path.exists(fmu_creation_path):
            os.makedirs(fmu_creation_path)
            fmu_folders.append(fmu_creation_path)

    print(f'List of created directories for idf creation: {idf_folders}')
    print(f'List of created directories for fmu creation: {fmu_folders}')
            
    return [idf_folders, fmu_folders]


def create_extra_idf_fmu_statements(fmu_path, current_fmu_filename, connected_fmu_paths, output_faces,  input_faces):

    # make sure we are not connecting this FMU to itself
    assert current_fmu_filename not in connected_fmu_paths

    # get the name of the current FMU and then its expected filepath
    current_fmu_instance_name = os.path.splitext(os.path.basename(os.path.dirname(fmu_path)))[0]
    current_fmu_filepath = os.path.join(fmu_path, f'{current_fmu_filename}.fmu')

    return_statements = f"""ExternalInterface,           !- Object to activate the external interface
 FUNCTIONALMOCKUPUNITEXPORT;              !- Name of external interface
 
"""
    
#     return_statements += f"""Output:SQLite,
#   SimpleAndTabular;                       !- Option Type

# """
    
#     for output_face in output_faces:
#         return_statements += f"""Output:Variable,*,{output_face.replace('.', '__')}_Surface_Outside_Face_Temperature,Hourly;  !- Include {output_face.replace('.', '_')}_Surface_Outside_Face_Temperature variable
# """
#     return_statements += """
# """

#     for connected_fmu_path in connected_fmu_paths:
# #         input_statements += f"""ExternalInterface:FunctionalMockupUnitImport:From:Variable,
# #     {connected_fmu_path},                !- FMU Name
# #     Surface Outside Face Temperature,      !- Output Variable Name
# #     {connected_fmu_path},       !- FMU Instance Name
# #     {connected_fmu_path} Surface Outside Face Temperature;    !- Variable Name for Retrieving the Value

# # """
        
# #         return_statements += f"""ExternalInterface:FunctionalMockupUnitImport,
# #     {connected_fmu_path},            !- FMU File Name could be fmu_path
# #     1500,                      !- FMU Timeout, check how much is needed
# #     0;                       !- FMU LoggingOn to see if debugging is enabled or not
    
# # """
#         pass

#     return_statements += f"""Output:JSON,
#     TimeSeriesAndTabular, !- timeseries data and tabular report data
#     Yes, !- turn on or off outputJSON
#     No, !- Output CBOR
#     No; !- turn off or on MessagePack output

# """

#     return_statements += f"""OutputControl:Files,
#   Yes, ! CSV
#   Yes, ! MTR
#   Yes, ! ESO
#   No , ! EIO
#   No , ! Tabular
#   No , ! SQLite
#   No , ! JSON
#   No , ! AUDIT
#   No , ! Zone Sizing
#   No , ! System Sizing
#   No , ! DXF
#   No , ! BND
#   No , ! RDD
#   No , ! MDD
#   No , ! MTD
#   Yes, ! END
#   No , ! SHD
#   No , ! DFS
#   No , ! GLHE
#   No , ! DelightIn
#   No , ! DelightELdmp
#   No , ! DelightDFdmp
#   No , ! EDD
#   No , ! DBG
#   No , ! PerfLog
#   No , ! SLN
#   No , ! SCI
#   No , ! WRL
#   No , ! Screen
#   No , ! ExtShd
#   No ; ! Tarcog

# """
    
    for output_face in output_faces:
        
        # Define the output of the FMU
        return_statements += f"""ExternalInterface:FunctionalMockupUnitExport:From:Variable,
{output_face},             !- EnergyPlus Key Value
Surface Outside Face Temperature,  !- EnergyPlus Variable Name
{output_face.replace('.', '__')}_Surface_Outside_Face_Temperature;                 !- FMU Variable Name

"""
    
        return_statements += f"""Output:Variable,
    {output_face},                    !- Key Value
    Surface Outside Face Temperature,   !- Variable Name
    TimeStep;                    !- Reporting Frequency

"""
            
    for input_face in input_faces:

#         return_statements += f"""ExternalInterface:Variable,
#     {input_face}_GB_Surface_Outside_Face_Temperature,                                   !- Name of Erl variable
#     1;                                             !- Initial value

# """
        return_statements += f"""ExternalInterface:FunctionalMockupUnitExport:To:Variable,
    {input_face.replace('.', '_')}_Surface_Outside_Face_Temperature,                       !- EnergyPlus Variable Name
    {input_face.replace('.', '__')}_Surface_Outside_Face_Temperature,                                   !- FMU Variable Name
    1;                                             !- Initial Value

"""
        
    return return_statements


from honeybee.model import Model
from honeybee.boundarycondition import Outdoors

def get_name_of_outdoor_bc_faces(path_hbjson_file):
    """ """
    hb_model_obj = Model.from_hbjson(path_hbjson_file)

    face_name_list=[]

    for room in hb_model_obj.rooms:
        for face in room.faces:
            if isinstance(face.boundary_condition,Outdoors):
                face_name_list.append(face.identifier)
    
    return face_name_list


def get_name_of_outdoor_bc_faces_list(paths_to_hbjson_param):
    """ """
    return {p: get_name_of_outdoor_bc_faces(p) for p in paths_to_hbjson_param}



def edit_idf_surfaces(file_path, content, type_of_edit='a'):
    try:
        with open(file_path, type_of_edit) as file:
            file.write('_____'.join(content))
        print(f"Content successfully appended to '{file_path}'.")
    except IOError as e:
        print(f"Error writing to file: {e}")


def edit_idf(file_path, content, type_of_edit='a'):
    try:
        with open(file_path, type_of_edit) as file:
            file.write(content)
        print(f"Content successfully appended to '{file_path}'.")
    except IOError as e:
        print(f"Error writing to file: {e}")


"""Steps are to create the IDF from the Honeybee JSON objects. Then """

path_fmu_conversion = '''C:\\Users\\alejandro.s\\Downloads\\EnergyPlusToFMU-v3.1.0\\Scripts\\EnergyPlusToFMU.py''' # '''C:\\Users\\alejandro.s\\Downloads\\EnergyPlusToFMU-v3.1.0\\Scripts\\EnergyPlusToFMU.py'''
path_idd = '''C:\\EnergyPlusV23-1-0\\Energy+.idd'''
fmi_version = 2  # default and only works for [1, 2]

path_to_fmus = "C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus"
paths_to_hbjson = [path_hbjson_file_twobuildingsfirst, path_hbjson_file_twobuildingssecond]

idf_folders, fmu_folders = create_folders(paths_to_hbjson, path_to_fmus)

# Get the name of the surface with outdoor boundary condition
name_of_faces_to_output_many = get_name_of_outdoor_bc_faces_list(paths_to_hbjson)

# dir_to_write_idf_in = "C:\\Users\\elie-medioni\\OneDrive\\OneDrive - Technion\\BUA\\test_elie"  # Elie

# dir_to_write_idf_in = "C:\\Users\\alejandro.s\\Documents\\sim_ep"  # TODO @Ale, add the path to the directory where you want to write the idf file

path_idf_list = []
# Create the IDFs for each building
for count, (idf_path, fmu_path, path_hbjson_file) in enumerate(zip(idf_folders, fmu_folders, paths_to_hbjson)):
    # Output is a E+ readable file
    (path_osm, path_idf) = from_hbjson_to_idf(idf_path, path_hbjson_file, path_epw_file, path_simulation_parameter)
    path_idf_list.append(path_idf)

    print(f'path_osm:{path_osm}\npath_idf:{path_idf}')
    print('-'*300)

    # Get the name of the surface with outdoor boundary condition
    name_of_faces_to_output = get_name_of_outdoor_bc_faces(path_hbjson_file)
    #Same for windows, to do later

    edit_idf_surfaces(os.path.join(idf_path, 'face_names.txt'), name_of_faces_to_output, type_of_edit='w')

    input_fmu_paths = [f for f in fmu_folders if f != fmu_path]

    # fmu_path, current_fmu_filename, connected_fmu_paths
    content = create_extra_idf_fmu_statements(
        fmu_path=fmu_path,
        # input_fmu_paths=input_fmu_paths,
        current_fmu_filename=os.path.splitext(os.path.basename(path_hbjson_file))[0],
        connected_fmu_paths=[pth for pth in fmu_folders if pth != fmu_path],
        output_faces=name_of_faces_to_output,
        input_faces=[vv for k,v in name_of_faces_to_output_many.items() for vv in v if k != path_hbjson_file]
    )
    edit_idf(path_idf, content)

    # test = fmu_path.replace('\\\\', '\\')
    # cmd = r'cd C:\Users\alejandro.s\Documents\two_building_eplus_fmus\model_1\fmu_creation'
    # # cmd = f"""cd {test}"""
    # run_cmdline(cmd)
    # print(f'Moved current directory to FMU path: {fmu_path}')

    # todo @Elie : add cd to the path of a temp folder, then move the fmu to their final destination
    cmd = f'''python {path_fmu_conversion} -i {path_idd} -w {path_epw_file} -a {fmi_version} {path_idf}'''
    run_cmdline(cmd)

    # Remove the remaining files that we do not need
    fmu_export_prep = 'C:\\Users\\alejandro.s\\AppData\Local\\Building_urban_analysis\\Scripts\\idf-to-fmu-export-prep-win.exe'
    get_address_size_prep = 'C:\\Users\\alejandro.s\\AppData\Local\\Building_urban_analysis\\Scripts\\util-get-address-size.exe'
    os.remove(fmu_export_prep)
    os.remove(get_address_size_prep)

    # Move the generated fmu file to our own directory
    shutil.move('C:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts\\in.fmu', fmu_path)

    print('&'*300)

    

# path_idf = 'C:\\Users\\alejandro.s\\Documents\\sim_ep\\run\\in.idf'

# Run E+
# directory = run_idf_windows_modified(path_idf, epw_file_path=path_epw_file, expand_objects=True,
#                              silent=False, path_energyplus_exe=path_ep)


# ALE's TURN!    WHAT IS IDD FILE AND WHERE IS IT AND SAME THING FOR THE WEATHER FILE?
# Create an E+ FMU
# python  <path-to-scripts-subdir>EnergyPlusToFMU.py  -i <path-to-idd-file> -w <path-to-weather-file> -a <fmi-version> <path-to-idf-file>
# # Windows: python  scriptDir\EnergyPlusToFMU.py  -i C:\eplus\Energy+.idd  -w test.epw  -a 2 test.idf





