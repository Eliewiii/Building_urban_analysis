"""

"""

example_parsed_dict = {
    "Context-1_Res_5-flrs": {
        "building_type": "Residential",
        "context_id": "1",
        "number_of_floors": "5",
        "no_ray_tracing": False,
        "mvfc": 0.1,
        "result_dict": {"BES": {"results": {"h+c": 1.0, "h+c+l": 2.0, "total": 3.0}}}
    },
    "Context-2_Of_10-flrs": {}
}


def parse_result_dict(result_dict: dict) -> dict:
    """
    Parse the result_dict to extract the relevant information
    param result_dict: dict, result_dict
    return: dict, parsed_dict
    """
    parsed_dict = {}
    for key,value in result_dict.items():
        parsed_dict[key] = {}
        # Extract building type
        if is_residential(key):
            parsed_dict[key]["building_type"] = "Residential"
        elif is_office(key):
            parsed_dict[key]["building_type"] = "Office"
        else:
            raise ValueError(f"Building type not recognized for key {key}")
        # Extract context id
        parsed_dict[key]["context_id"] = get_context_id(key)
        # Extract number of floors
        parsed_dict[key]["number_of_floors"] = get_nb_of_floors(key)
        # Extract no_ray_tracing
        parsed_dict[key]["no_ray_tracing"] = value["context_selection"]["second_pass"]['no_ray_tracing']
        # Extract mvfc
        parsed_dict[key]["mvfc"] = value["context_selection"]["first_pass"]['mvfc']
        # Extract result_dict
        parsed_dict[key]["result_dict"] = value
    return parsed_dict


def plot_error_raytracing_vs_mvfc(result_dict, buidling_type="All", context_id="All", number_of_floors="All"):
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
        if (buidling_type == "residential" and not is_residential(key)) or (
                buidling_type == "office" and not is_office(key)):
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
    return result_dict_key.split("-flrs")[0].split("-")[1]

def is_context_id(result_dict_key, context_id):
    """
    Check if the context id is the one we are looking for
    param result_dict_key: dict, result_dict_key
    context_id: str, "1", "2" or "3"
    return: bool, True if the context id is the one we are looking for
    """
    if "Context-" + context_id in result_dict_key:
        return True
    return False


def has_nb_of_floor(result_dict_key, number_of_floors):
    """
    Check if the number of floors is the one we are looking for
    param result_dict_key: dict, result_dict_key
    number_of_floors: str, "5", "10", "15", "20", "25" or "30"
    return: bool, True if the number of floors is the one we are looking for
    """
    if "_" + number_of_floors + "-flrs" in result_dict_key:
        return True
    return False
