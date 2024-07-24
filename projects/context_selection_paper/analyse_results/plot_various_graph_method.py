"""
Functions to plot all the graphs
"""
import os
import json

from projects.context_selection_paper.box_chart_methods.plot_box_chart import plot_xlog_box_chart
from projects.context_selection_paper.analyse_results.parse_result_dict import \
    parse_result_dict, get_reference_value


def read_json_dict(path_to_result_dict: str):
    """
    Read a JSON file and return the dictionary.
    param path_to_result_dict: String. The path to the result dictionary.
    return: Dictionary. The result dictionary.
    """
    if not os.path.exists(path_to_result_dict):
        print(f"File not found: {path_to_result_dict}")
    else:
        with open(path_to_result_dict, 'r') as f:
            try:
                result_dict = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading JSON file: {e}")
    return result_dict


def plot_bes_error_compared_to_ref_vs_mvfc(path_to_result_dict: str, building_type="All", no_raytracing=False,
                                           result_key: str = "total", base_width: float = 0.1,
                                           fig_height: float = 6.,
                                           fig_width: float = 9.):
    """
    Plot the error compared to the reference vs the MVFC. in ansolute value of the error
    param path_to_result_dict: String. The path to the result dictionary.
    param building_type: String. The building type to plot. "Residential", "Office" or "All"
    param no_raytracing: Bool. If True, the raytracing results are not plotted.
    param result_key: String. The result key to plot, it can be "total", "h+c" or "h+c+l"
    param base_width: Float. The width of the boxes in the chart.
    param fig_height: Float. The height of the figure.
    param fig_width: Float. The width of the figure.
    """
    # Read the result dictionary
    result_dict = read_json_dict(path_to_result_dict)
    # Parse dictionary
    parsed_dict = parse_result_dict(result_dict)
    # Differentiate between raytracing and no raytracing
    if no_raytracing:
        raytracing_key = "no_ray_tracing"
    else:
        raytracing_key = "ray_tracing"
    # Initialize data dictionary
    data_dict = {}  # {MVFC: [errors]}

    for sim_building_value in parsed_dict.values():
        if building_type != "All" and sim_building_value["building_type"] != building_type:
            continue
        bes_reference_value = get_reference_value(sub_parsed_dict=sim_building_value,
                                                  no_raytracing=no_raytracing, result_type='BES',
                                                  result_key=result_key)
        for mvfc, result_dict in sim_building_value[raytracing_key].items():
            if mvfc not in data_dict:
                data_dict[mvfc] = []
            error = abs(1 - result_dict["BES"]["results"][result_key] / bes_reference_value) * 100
            # error = (1 - result_dict["BES"]["results"][result_key] / bes_reference_value) * 100
            data_dict[mvfc].append(error)
            # # testing
            # if mvfc<0.003 and error>2:
            #     print( f"Context_{sim_building_value['context_id']}_nbFl_{sim_building_value['number_of_floors']}")

    # Sort the data to make sure there is no shift between x_postion and the data
    x_positions = sorted(data_dict.keys())
    data = [data_dict[x] for x in x_positions]

    plot_xlog_box_chart(data=data, x_positions=x_positions, x_label="MVFC",
                        y_label="Error BES [%]", title=f"Error_compared_to_reference_{result_key}",
                        base_width=base_width, fig_height=fig_height, fig_width=fig_width)


def plot_bes_error_compared_to_no_raytracing_vs_mvfc(path_to_result_dict: str, building_type="All",
                                                     result_key: str = "total", base_width: float = 0.1,
                                                     fig_height: float = 6.,
                                                     fig_width: float = 9.):
    """
    Plot the error compared to the reference vs the MVFC. in ansolute value of the error
    param path_to_result_dict: String. The path to the result dictionary.
    param building_type: String. The building type to plot. "Residential", "Office" or "All"
    param result_key: String. The result key to plot, it can be "total", "h+c" or "h+c+l"
    param base_width: Float. The width of the boxes in the chart.
    param fig_height: Float. The height of the figure.
    param fig_width: Float. The width of the figure.
    """
    # Read the result dictionary
    result_dict = read_json_dict(path_to_result_dict)
    # Parse dictionary
    parsed_dict = parse_result_dict(result_dict)

    # Initialize data dictionary
    data_dict = {}  # {MVFC: [errors]}

    for sim_building_value in parsed_dict.values():
        if building_type != "All" and sim_building_value["building_type"] != building_type:
            continue
        for mvfc in list(sim_building_value["ray_tracing"].keys()):
            if mvfc in list(sim_building_value["no_ray_tracing"].keys()):
                result_dict_rt = sim_building_value["ray_tracing"][mvfc]
                result_dict_no_rt = sim_building_value["no_ray_tracing"][mvfc]
                if mvfc not in data_dict:
                    data_dict[mvfc] = []
                error = abs(
                    1 - result_dict_rt["BES"]["results"][result_key] / result_dict_no_rt["BES"]["results"][
                        result_key]) * 100
                data_dict[mvfc].append(error)

    # Sort the data to make sure there is no shift between x_postion and the data
    x_positions = sorted(data_dict.keys())
    data = [data_dict[x] for x in x_positions]

    plot_xlog_box_chart(data=data, x_positions=x_positions, x_label="MVFC",
                        y_label="Error BES [%]", title=f"Error_compared_to_no_raytracing_{result_key}",
                        base_width=base_width, fig_height=fig_height, fig_width=fig_width)


def plot_computation_time_compared_to_ref_vs_mvfc(path_to_result_dict: str, building_type="All",
                                                  no_raytracing=False, base_width: float = 0.1,
                                                  fig_height: float = 6.,
                                                  fig_width: float = 9.):
    """
    Plot the error compared to the reference vs the MVFC. in ansolute value of the error
    param path_to_result_dict: String. The path to the result dictionary.
    param building_type: String. The building type to plot. "Residential", "Office" or "All"
    param no_raytracing: Bool. If True, the raytracing results are not plotted.
    param base_width: Float. The width of the boxes in the chart.
    param fig_height: Float. The height of the figure.
    param fig_width: Float. The width of the figure.
    """
    # Read the result dictionary
    result_dict = read_json_dict(path_to_result_dict)
    # Parse dictionary
    parsed_dict = parse_result_dict(result_dict)
    # Differentiate between raytracing and no raytracing
    if no_raytracing:
        raytracing_key = "no_ray_tracing"
    else:
        raytracing_key = "ray_tracing"
    # Initialize data dictionary
    data_dict = {}  # {MVFC: [errors]}

    for sim_building_value in parsed_dict.values():
        if building_type != "All" and sim_building_value["building_type"] != building_type:
            continue
        duration_reference_value = get_reference_value(sub_parsed_dict=sim_building_value,
                                                       no_raytracing=no_raytracing, result_type="duration",
                                                       result_key="BEM+Context_Selection")
        for mvfc, result_dict in sim_building_value[raytracing_key].items():
            if mvfc not in data_dict:
                data_dict[mvfc] = []
            BEM_duration = sim_building_value[raytracing_key][mvfc]["BES"]["duration"]
            first_pass_duration = sim_building_value[raytracing_key][mvfc]["context_selection"]["first_pass"][
                "duration"]
            second_pass_duration = \
                sim_building_value[raytracing_key][mvfc]["context_selection"]["second_pass"][
                    "duration"]
            total_duration = BEM_duration + first_pass_duration + second_pass_duration
            error = (total_duration / duration_reference_value - 1) * 100
            data_dict[mvfc].append(error)

    # Sort the data to make sure there is no shift between x_postion and the data
    x_positions = sorted(data_dict.keys())
    data = [data_dict[x] for x in x_positions]

    plot_xlog_box_chart(data=data, x_positions=x_positions, x_label="MVFC",
                        y_label="Computation_time difference [%]",
                        title=f"Computation_time_compared_to_reference",
                        base_width=base_width, fig_height=fig_height, fig_width=fig_width)


if __name__ == "__main__":
    path_to_result_dict = r"C:\Users\elie-medioni\OneDrive\OneDrive - Technion\Ministry of Energy Research\Papers\CheckContext\Simulations_Elie\results\Saved_results\results_context_filter_lca_lab_5_ext_2.json"
    plot_bes_error_compared_to_ref_vs_mvfc(path_to_result_dict,
                                           building_type="Residential",
                                           no_raytracing=False,
                                           result_key="h+c",
                                           base_width=0.03,
                                           fig_height=10., fig_width=15.)
    # plot_bes_error_compared_to_no_raytracing_vs_mvfc(path_to_result_dict,
    #                                                  building_type="Residential",
    #                                                  result_key="h+c",
    #                                                  base_width=0.01,
    #                                                  fig_height=10., fig_width=15.)
    # plot_bes_error_compared_to_ref_vs_mvfc(path_to_result_dict,
    #                                        building_type="Office",
    #                                        no_raytracing=False,
    #                                        result_key="h+c",
    #                                        base_width=0.01,
    #                                        fig_height=10., fig_width=15.)
    # plot_computation_time_compared_to_ref_vs_mvfc(path_to_result_dict,
    #                                               building_type="Office",
    #                                               no_raytracing=False,
    #                                               base_width=0.05,
    #                                               fig_height=10., fig_width=15.)
