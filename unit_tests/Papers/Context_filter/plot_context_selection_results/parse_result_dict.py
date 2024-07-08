"""

"""
"""
example_parsed_dict = {
    "Res_5-flrs_NoContext-1": {
        "building_type": "Residential",
        "context_id": "1",
        "number_of_floors": "5",
        "no_ray_tracing": {0.99:{result dict},0.1:{...},
        "ray_tracing": {0.99:{result dict},0.1:{},
    },
    "Context-2_Of_10-flrs": {"no_ray_tracing": {0.99:{result dict},0.1:{},}
}
"""


def parse_result_dict(result_dict: dict) -> dict:
    """
    Parse the result_dict to extract the relevant information
    param result_dict: dict, result_dict
    return: dict, parsed_dict
    """
    parsed_dict = {}
    for key, value in result_dict.items():
        # Extract building type
        if is_residential(key):
            building_type = "Residential"
        elif is_office(key):
            building_type = "Office"
        else:
            raise ValueError(f"Building type not recognized for key {key}")
        # Extract context id
        context_id = get_context_id(key)
        # Extract number of floors
        nb_floor = get_nb_of_floors(key)
        # Building id
        building_id = f"Context-{context_id}_{building_type}_{nb_floor}-flrs"
        # Initialize the building id
        if building_id not in parsed_dict:
            parsed_dict[building_id] = {}
            parsed_dict[building_id]["building_type"] = building_type
            parsed_dict[building_id]["context_id"] = context_id
            parsed_dict[building_id]["number_of_floors"] = nb_floor
            parsed_dict[building_id]["no_ray_tracing"] = {}
            parsed_dict[building_id]["ray_tracing"] = {}
        # Extract the results
        if value["context_selection"]["second_pass"]["no_ray_tracing"]:
            parsed_dict[building_id]["no_ray_tracing"][
                value["context_selection"]["first_pass"]["mvfc"]] = value
        else:
            parsed_dict[building_id]["ray_tracing"][value["context_selection"]["first_pass"]["mvfc"]] = value

    return parsed_dict


def get_reference_value(sub_parsed_dict: dict, no_raytracing: bool, result_type, result_key) -> float:
    """
    Get the reference value for a given building
    param sub_parsed_dict: dict, sub_parsed_dict, one value of the global parsed dict
    param no_raytracing: bool, True if no ray tracing
    param result_type: str, can be within "BES", "duration"
    param result_key: str, result key, for energy consumption, it can be "total", "h+c" or "h+c+l"
    return: float, reference value
    """
    if no_raytracing:
        raytracing_key = "no_ray_tracing"
    else:
        raytracing_key = "ray_tracing"

    if result_type == "BES":
        mvfc = get_minimum_mvfc(parsed_dict_sub_res_dict=sub_parsed_dict[raytracing_key])
        reference_value = sub_parsed_dict[raytracing_key][mvfc]["BES"]["results"][result_key]
        return reference_value

    if result_type == "duration":
        mvfc = get_maximum_mvfc(parsed_dict_sub_res_dict=sub_parsed_dict[raytracing_key])
        BEM_duration = sub_parsed_dict[raytracing_key][mvfc]["BES"]["duration"]
        first_pass_duration = sub_parsed_dict[raytracing_key][mvfc]["context_selection"]["first_pass"]["duration"]
        second_pass_duration = sub_parsed_dict[raytracing_key][mvfc]["context_selection"]["second_pass"][
            "duration"]

        if result_key == "BEM":
            return BEM_duration
        if result_key == "BEM+Context_Selection":
            return BEM_duration + first_pass_duration + second_pass_duration

    else:
        raise ValueError(f"Result type {result_type} not a possible option")


def get_minimum_mvfc(parsed_dict_sub_res_dict: dict) -> float:
    """
    Get the minimum MVFC for a given building
    """
    return min(parsed_dict_sub_res_dict.keys())


def get_maximum_mvfc(parsed_dict_sub_res_dict: dict) -> float:
    """
    Get the Maximum MVFC for a given building
    """
    return max(parsed_dict_sub_res_dict.keys())


def is_residential(result_dict_key):
    """
    Check if the building is residential
    param result_dict_key: dict, result_dict_key
    return: bool, True if the building is residential
    """
    if "Res_" in result_dict_key:
        return True
    return False


def is_office(result_dict_key):
    """
    Check if the building is office
    param result_dict_key: dict, result_dict_key
    return: bool, True if the building is office
    """
    if "Of_" in result_dict_key:
        return True
    return False


def get_context_id(result_dict_key):
    """
    Get the context id
    param result_dict_key: dict, result_dict_key
    return: str, "1", "2" or "3"
    """
    return result_dict_key.split("Context-")[1].split("_")[0]


def get_nb_of_floors(result_dict_key):
    """
    Get the number of floors
    param result_dict_key: dict, result_dict_key
    return: str, "5", "10", "15", "20", "25" or "30"
    """
    return result_dict_key.split("-flrs")[0].split("_")[-1]
