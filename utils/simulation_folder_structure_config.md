# Simulation folder structure
This folder, that can be generated and/or loaded anywhere in the computer (up to the user), contains has the following architecture:

```bash
.
├── gh_components_logs     # For the logs of the GH components
    ├── component_name_1.log         # One file per component
    ├── component_name_2.log         
    ├── ...
├── temporary_files_folder  # For the all simulation generating temporary files
    ├── ...         # Can have any structure, and are usually deleted after the simulation as they can be very large
├── UBES_simulation    # Contains shapefiles for the dataset
    ├── building_1     # One folder per Building
        ├── building_1.err         
        ├── building_1.sql
        ├── in.idf         
        ├── ...
    ├── building_2            
    ├── ...
Irradiance_and_BIPV_simulation    # Contains shapefiles for the dataset
    ├── building_1     # One folder per Building
        ├── building_1_bipv_results.csv         
        ├── roof.ill
        ├── roof_sun-up-hours.txt
        ├── facades.ill
        ├── facades_sun-up-hours.txt
        ├── building_1_bipv_result_dict.csv
        ├── ...
    ├── building_2     
    ├── uc_scenario_1     # One folder per Urban Canopy Scenario
        ├── uc_scenario_1_bipv_results.csv        
        ├── uc_scenario_1_kpis_intermediate_results.csv     
        ├── uc_scenario_1_kpis_results.csv    
    ├── uc_scenario_2
    ├── ...
LWR
  ├── FMUS
    ├── name_folder_fmu_1
      ├── ...
        ├── in.fmu 
urban_canopy.pkl
urban_canopy.json
```

Not all the folders or files might not have been created already depending on the simulation steps that were run.