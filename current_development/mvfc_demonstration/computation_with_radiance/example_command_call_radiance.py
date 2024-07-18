import os

path_radiance = r"D:\Elie\PhD\Software\Radiance\bin"
path_rfluxmtx = r"D:\Elie\PhD\Software\Radiance\bin\rfluxmtx"

current_dir=r"C:\Users\elie-medioni\AppData\Local\Building_urban_analysis\Scripts\current_development\mvfc_demonstration\computation_with_radiance"

path_emitter_rad_file = os.path.join(current_dir, "example_emitter.rad")
path_receptor_rad_file = os.path.join(current_dir, "example_receptor.rad")


output_file = os.path.join(current_dir, "output.txt")

nb_ray = 100000
#


command = f'rfluxmtx -h- -ab 0 -c {nb_ray} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_receptor_rad_file}" > "{output_file}"'
print(command)
res = os.system(command)
print (res)

# command = f'CD "{path_radiance}" & "{path_rfluxmtx}" -h- -ab 0 -c {nb_ray} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"'
# print(command)
# res = os.system(command)

# command = os.system(
#     f'CD "{path_radiance}" & "{path_rfluxmtx}" -h- -ab 0 -c {nb_ray} ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"')


# command = f'rfluxmtx.exe -h- -ab 0 -c {nb_ray} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + f'"{path_emitter_rad_file}" "{path_receptor_rad_file}" > "{output_file}"'

