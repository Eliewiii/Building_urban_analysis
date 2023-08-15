from fmpy import dump, simulate_fmu, read_model_description


fmu_1 = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_1\\fmu_creation\\in.fmu'  # 'C:\\Users\\alejandro.s\\AppData\\Local\\Building_urban_analysis\\Scripts\\long_wave_radiation_coupling\\Ale\\in.fmu'
fmu_2 = 'C:\\Users\\alejandro.s\\Documents\\two_building_eplus_fmus\\model_2\\fmu_creation\\in.fmu'

dump(fmu_1)

model_description = read_model_description(fmu_1)

# parameters = [v for v in model_description.modelVariables if v.causality == 'parameter']

result = simulate_fmu(fmu_1)  # simulate the FMU
# from fmpy.util import plot_result  # import the plot function
# plot_result(result)

