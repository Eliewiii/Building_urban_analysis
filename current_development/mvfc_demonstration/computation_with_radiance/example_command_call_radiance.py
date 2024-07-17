import os

path_radiance = r"D:\Elie\PhD\Software\Radiance\bin"
path_rfluxmtx = r"C:\Program Files\ladybug_tools\radiance\bin\rfluxmtx.exe"

current_dir=r"C:\Users\elie-medioni\AppData\Local\Building_urban_analysis\Scripts\current_development\mvfc_demonstration\computation_with_radiance"

path_emitter_rad_file = os.path.join(current_dir, "example_emitter.rad")
path_receptor_rad_file = os.path.join(current_dir, "example_receptor.rad")


output_file = os.path.join(current_dir, "output.txt")

nb_ray = 100000
#
# command = os.system(
#     f'CD "{path_radiance}" & "{path_rfluxmtx}" -h- -ab 0 -c {nb_ray} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"')

# command = os.system(
#     f'CD "{path_radiance}" & "{path_rfluxmtx}" -h- -ab 0 -c {nb_ray} ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"')


command = os.system(
    f'rfluxmtx -h- -ab 0 -c {nb_ray} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"')
