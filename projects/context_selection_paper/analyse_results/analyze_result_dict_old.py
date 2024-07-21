import os
import json
import numpy as np
import matplotlib.pyplot as plt


def plot_computation_time_vs_mvfc(result_dict,buidling_type="All",context_id="All",number_of_floors="All"):
    """
    Plot computation time vs MVFC
    param result_dict: dict, result_dic
    buidling_type: str, "residential", "office" or "All"
    context_id: str, "All" or "1", "2" or "3"
    number_of_floors: str, "All" or "5", "10", "15", "20", "25" or "30"
    """
    mvfc = []
    computation_time = []
    nb_surfaces = []
    for key in result_dict:
        # Filter by building type
        if (buidling_type == "residential" and not is_residential(key)) or (buidling_type == "office" and not is_office(key)):
            continue
        # Filter by context id
        if context_id != "All" and not is_context_id(key, context_id):
            continue
        # Filter by number of floors
        if number_of_floors != "All" and not has_nb_of_floor(key, number_of_floors):
            continue
        # Add the values to the lists
        try:
            if result_dict[key]["context_selection"]["second_pass"]['no_ray_tracing'] == True:
                continue
            mvfc.append(result_dict[key]["context_selection"]["first_pass"]['mvfc'])
            computation_time.append(result_dict[key]["BES"]['duration'])
            nb_surfaces.append(result_dict[key]["context_selection"]["second_pass"]['nb_selected_shades'])
        except KeyError as e:
            print(f"KeyError: {e}")
            continue

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = 'tab:blue'
    ax1.set_xlabel('MVFC', fontsize=14)
    ax1.set_ylabel('BES Computation Time (s)', color=color1, fontsize=14)
    ax1.plot(mvfc, computation_time, 'o', color=color1, markerfacecolor='blue', markersize=8)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xscale('log')
    ax1.set_ylim(bottom=0)
    ax1.grid(True)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color2 = 'tab:green'
    ax2.set_ylabel('Number of Surfaces', color=color2, fontsize=14)
    ax2.plot(mvfc, nb_surfaces, 's', color=color2, markerfacecolor='green', markersize=8)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(bottom=0)

    plt.title('Computation Time and Number of Surfaces vs MVFC', fontsize=16)

    fig.tight_layout(rect=[0, 0, 1, 0.95])  # adjust the rect parameter to fit the title
    plt.subplots_adjust(top=0.85)  # adjust the top spacing to fit the title

    plt.show()

    # Save the plot as an image file
    # plt.savefig("computation_time_vs_mvfc.png")


def plot_error_raytracing_vs_mvfc(result_dict,buidling_type="All",context_id="All",number_of_floors="All"):
    """
    Plot computation time vs MVFC
    param result_dict: dict, result_dic
    buidling_type: str, "residential", "office" or "All"
    context_id: str, "All" or "1", "2" or "3"
    number_of_floors: str, "All" or "5", "10", "15", "20", "25" or "30"
    """
    mvfc = []
    en_cons_with_raytracing = {}
    en_cons_no_raytracing = {}
    for key in result_dict:
        # Filter by building type
        if (buidling_type == "residential" and not is_residential(key)) or (buidling_type == "office" and not is_office(key)):
            continue
        # Filter by context id
        if context_id != "All" and not is_context_id(key, context_id):
            continue
        # Filter by number of floors
        if number_of_floors != "All" and not has_nb_of_floor(key, number_of_floors):
            continue
        # Add the values to the lists
        try:
            if result_dict[key]["context_selection"]["first_pass"]['mvfc'] not in mvfc:
                mvfc.append(result_dict[key]["context_selection"]["first_pass"]['mvfc'])
            if result_dict[key]["context_selection"]["second_pass"]['no_ray_tracing'] == True:
                en_cons_no_raytracing[result_dict[key]["context_selection"]["first_pass"]['mvfc']] = {
                    "h+c": result_dict[key]["BES"]["results"]["h+c"],
                    "h+c+l": result_dict[key]["BES"]["results"]["h+c+l"],
                    "total": result_dict[key]["BES"]["results"]["total"]}

            else:
                en_cons_with_raytracing[result_dict[key]["context_selection"]["first_pass"]['mvfc']] = {
                    "h+c": result_dict[key]["BES"]["results"]["h+c"],
                    "h+c+l": result_dict[key]["BES"]["results"]["h+c+l"],
                    "total": result_dict[key]["BES"]["results"]["total"]}

        except KeyError as e:
            print(f"KeyError: {e}")
            continue

    error_hc = [abs(1 - en_cons_no_raytracing[mvfc_val]["h+c"] / en_cons_with_raytracing[mvfc_val]["h+c"]) for
                mvfc_val in mvfc]
    error_hcl = [
        abs(1 - en_cons_no_raytracing[mvfc_val]["h+c+l"] / en_cons_with_raytracing[mvfc_val]["h+c+l"]) for
        mvfc_val in mvfc]
    error_total = [
        abs(1 - en_cons_no_raytracing[mvfc_val]["total"] / en_cons_with_raytracing[mvfc_val]["total"]) for
        mvfc_val in mvfc]

    # Plot total energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_total, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error Total', fontsize=14)
    plt.title('', fontsize=16)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()
    # Plot H-C energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_hc, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error HC', fontsize=14)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()
    # Plot H-C+L energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_hcl, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error HCL', fontsize=14)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()


def plot_error_all_surfaces_vs_mvfc(result_dict,buidling_type="All",context_id="All",number_of_floors="All"):
    """
    Plot computation time vs MVFC
    param result_dict: dict, result_dic
    buidling_type: str, "residential", "office" or "All"
    context_id: str, "All" or "1", "2" or "3"
    ,number_of_floors="All"
    """
    mvfc = []
    en_cons = {}
    for key in result_dict:
        # Filter by building type
        if (buidling_type == "residential" and not is_residential(key)) or (buidling_type == "office" and not is_office(key)):
            continue
        # Filter by context id
        if context_id != "All" and not is_context_id(key, context_id):
            continue
        # Filter by number of floors
        if number_of_floors != "All" and not has_nb_of_floor(key, number_of_floors):
            continue
        # Add the values to the lists
        try:
            if result_dict[key]["context_selection"]["first_pass"]['mvfc'] not in mvfc:
                mvfc.append(result_dict[key]["context_selection"]["first_pass"]['mvfc'])
            if result_dict[key]["context_selection"]["second_pass"]['no_ray_tracing'] == True:
                continue

            else:
                en_cons[result_dict[key]["context_selection"]["first_pass"]['mvfc']] = {
                    "h+c": result_dict[key]["BES"]["results"]["h+c"],
                    "h+c+l": result_dict[key]["BES"]["results"]["h+c+l"],
                    "total": result_dict[key]["BES"]["results"]["total"]}

        except KeyError as e:
            print(f"KeyError: {e}")
            continue

    min_mvfc = min(mvfc)

    error_hc = [abs(1 - en_cons[mvfc_val]["h+c"] / en_cons[min_mvfc]["h+c"])*100 for mvfc_val in mvfc]
    error_hcl = [abs(1 - en_cons[mvfc_val]["h+c+l"] / en_cons[min_mvfc]["h+c+l"])*100 for mvfc_val in mvfc]
    error_total = [abs(1 - en_cons[mvfc_val]["total"] / en_cons[min_mvfc]["total"])*100 for mvfc_val in mvfc]

    # Plot total energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_total, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error [%]', fontsize=14)
    plt.title('Error of in the Total energy consumption compared to the lowest mvfc alternative', fontsize=16)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()
    # Plot H-C energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_hc, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error HC', fontsize=14)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()
    # Plot H-C+L energy consumption
    plt.figure(figsize=(10, 6))
    plt.plot(mvfc, error_hcl, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('MVFC', fontsize=14)
    plt.ylabel('Error HCL', fontsize=14)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)
    plt.show()


def plot_computation_time_vs_number_of_surfaces(result_dict,buidling_type="All",context_id="All",number_of_floors="All"):
    """
    Plot computation time vs MVFC
    param result_dict: dict, result_dic
    buidling_type: str, "residential", "office" or "All"
    context_id: str, "All" or "1", "2" or "3"
    number_of_floors: str, "All" or "5", "10", "15", "20", "25" or "30"
    """
    nb_surf = []
    computation_time = []
    for key in result_dict:
        # Filter by building type
        if (buidling_type == "residential" and not is_residential(key)) or (buidling_type == "office" and not is_office(key)):
            continue
        # Filter by context id
        if context_id != "All" and not is_context_id(key, context_id):
            continue
        # Filter by number of floors
        if number_of_floors != "All" and not has_nb_of_floor(key, number_of_floors):
            continue
        # Add the values to the lists
        try:
            nb_surf.append(result_dict[key]["context_selection"]["second_pass"]['nb_selected_shades'])
            computation_time.append(result_dict[key]["BES"]['duration'])
        except KeyError as e:
            print(f"KeyError: {e}")
            continue

    plt.figure(figsize=(10, 6))
    plt.plot(nb_surf, computation_time, 'o', color='blue', markerfacecolor='red', markersize=8)
    plt.xlabel('Number of Surfaces', fontsize=14)
    plt.ylabel('BES Computation Time (s)', fontsize=14)
    plt.title('Computation Time vs Number of Surfaces', fontsize=16)
    # plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.grid(True)

    plt.show()

    # Save the plot as an image file
    # plt.savefig("computation_time_vs_mvfc.png")

def is_residential(result_dict_key):
    """
    Check if the building is residential
    param result_dict_key: dict, result_dict_key
    return: bool, True if the building is residential
    """
    if "Res" in result_dict_key:
        return True
    return False

def is_office(result_dict_key):
    """
    Check if the building is office
    param result_dict_key: dict, result_dict_key
    return: bool, True if the building is office
    """
    if "Of" in result_dict_key:
        return True
    return False

def is_context_id(result_dict_key, context_id):
    """
    Check if the context id is the one we are looking for
    param result_dict_key: dict, result_dict_key
    context_id: str, "1", "2" or "3"
    return: bool, True if the context id is the one we are looking for
    """
    if "Context-"+context_id in result_dict_key:
        return True
    return False

def has_nb_of_floor(result_dict_key, number_of_floors):
    """
    Check if the number of floors is the one we are looking for
    param result_dict_key: dict, result_dict_key
    number_of_floors: str, "5", "10", "15", "20", "25" or "30"
    return: bool, True if the number of floors is the one we are looking for
    """
    if "_"+number_of_floors+"-flrs" in result_dict_key:
        return True
    return False




if __name__ == "__main__":
    path_to_result_dict = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\results\results_context_filter_lca_lab_5_copy.json"
    if not os.path.exists(path_to_result_dict):
        print(f"File not found: {path_to_result_dict}")
    else:
        with open(path_to_result_dict, 'r') as f:
            try:
                result_dict = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading JSON file: {e}")
            else:
                # plot_computation_time_vs_mvfc(result_dict, buidling_type="residential", context_id="All", number_of_floors="5")
                plot_error_all_surfaces_vs_mvfc(result_dict, buidling_type="residential", context_id="1", number_of_floors="30")
                # plot_error_raytracing_vs_mvfc(result_dict)
                # plot_computation_time_vs_number_of_surfaces(result_dict,buidling_type="residential")
