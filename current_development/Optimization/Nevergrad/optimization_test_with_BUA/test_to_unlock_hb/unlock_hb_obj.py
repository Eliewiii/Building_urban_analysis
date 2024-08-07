from honeybee.model import Model
from honeybee_energy.schedule.ruleset import ScheduleRuleset

from concurrent.futures import ProcessPoolExecutor

def load_hbjson_file(path_hbjson_file):
    """
    Function to load the honeybee model object from a hbjson file.
    """

    return Model.from_hbjson(path_hbjson_file)


def unlock_hb_model(hb_model_obj):
    """
    Function to unlock the honeybee model object.
    """
    # unlock the materials
    for mat in hb_model_obj.properties.energy.materials:
        print(mat)
        mat.unlock()
    # unlock the constructions
    for con in hb_model_obj.properties.energy.constructions:
        con.unlock()
    # unlock the construction_sets
    for cs in hb_model_obj.properties.energy.construction_sets:
        cs.unlock()
    # unlock the schedules
    for sch in hb_model_obj.properties.energy.schedules:
        sch.unlock()
        if isinstance(sch, ScheduleRuleset):
            for day_sch in sch.day_schedules:
                day_sch.unlock()
    # unlock the program
    for prg in hb_model_obj.properties.energy.program_types:
        prg.unlock()







def worker(hb_object):
    print (hb_object.identifier)
    return hb_object.identifier

# Simulate using ProcessPoolExecutor




if __name__ == "__main__":
    path_hbjson_file = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\BIPV extended paper\Simulations\Test_Nevergrad\hbjsons\Buil_TA_0.hbjson"
    hb_model_obj = load_hbjson_file(path_hbjson_file)
    unlock_hb_model(hb_model_obj)

    with ProcessPoolExecutor() as executor:
        future = executor.submit(worker, hb_model_obj)
        result = future.result()
