

result_dict1 = {
    "energy_harvested": {"yearly": [100.0, 200.0], "total": 500.0},
    # ... (other nested dictionaries and lists of floats)
    "dmfa_waste": {"yearly": [20.0, 30.0], "total": 80.0}
}

result_dict2 = {
    "energy_harvested": {"yearly": [150.0, 250.0], "total": 600.0},
    # ... (other nested dictionaries and lists of floats)
    "dmfa_waste": {"yearly": [30.0, 40.0], "total": 100.0}
}

result_dict3 = {
    "energy_harvested": {"yearly": [50.0, 100.0,200], "total": 300.0},
    # ... (other nested dictionaries and lists of floats)
    "dmfa_waste": {"yearly": [10.0, 20.0,30.0], "total": 40.0}
}





def sum_dicts(dict_1, dict_2,starting_years,earliest_year,latest_year):
    """
    Sum the values dictionnaries
    """

    result_dict = {}
    for key in dict_1:
        if isinstance(dict_1[key], dict):
            result_dict[key] = sum_dicts(dict_1[key], dict_2[key],starting_years,earliest_year,latest_year)
        elif isinstance(dict_1[key], list):
            list_1 = [0.0] * (latest_year-earliest_year+1 )
            list_1[starting_years[0]-earliest_year:starting_years[0]-earliest_year+len(dict_1[key])] = dict_1[key]
            list_2 = [0.0] * (latest_year-earliest_year+1 )
            list_2[starting_years[1]-earliest_year:starting_years[1]-earliest_year+len(dict_2[key])] = dict_2[key]
            result_dict[key] = [x + y for x, y in zip(list_1, list_2)]
        else:  # assuming ints or floats
            result_dict[key] = dict_1[key] + dict_2[key]

    return result_dict

def boudary_years(data_dicts,starting_years):
    # Find the earliest and latest years across all dictionaries
    earliest_year = min(starting_years)
    latest_year = max(
        year + len(data_dict["energy_harvested"]["yearly"]) - 1
        for year, data_dict in zip(starting_years, data_dicts)
    )
    return earliest_year,latest_year


starting_years = [2020, 2022]

earliest_year,latest_year= boudary_years([result_dict1, result_dict3], starting_years)

earliest_year = earliest_year -1

result = sum_dicts(result_dict1, result_dict3, starting_years,earliest_year,latest_year)
print(result)



