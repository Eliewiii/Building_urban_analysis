

result_dict1 = {
    "energy_harvested": {"yearly": [100.0, 200.0],"cumulative":None, "total": None},
    # ... (other nested dictionaries and lists of floats)
    "dmfa_waste": {"yearly": [20.0, 30.0],"cumulative":None, "total": None}
}

result_dict2 = {
    "energy_harvested": {"yearly": [150.0, 250.0], "total": 600.0},
    # ... (other nested dictionaries and lists of floats)
    "dmfa_waste": {"yearly": [30.0, 40.0], "total": 100.0}
}

result_dict3 = {
    "energy_harvested": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
    "lca_primary_energy": {
        "material_extraction_and_manufacturing": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "transportation": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "recycling": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "total": {"yearly": [100.0, 200.0], "cumulative": None, "total": None}
    },
    "lca_carbon_footprint": {
        "material_extraction_and_manufacturing": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "transportation": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "recycling": {"yearly": [100.0, 200.0], "cumulative": None, "total": None},
        "total": {"yearly": [100.0, 200.0], "cumulative": None, "total": None}
    },
    "dmfa_waste": {"yearly": [], "cumulative": None, "total": None}
}







def boudary_years(data_dicts,starting_years):
    # Find the earliest and latest years across all dictionaries
    earliest_year = min(starting_years)
    latest_year = max(
        year + len(data_dict["energy_harvested"]["yearly"]) - 1
        for year, data_dict in zip(starting_years, data_dicts)
    )
    return earliest_year,latest_year

def compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict):
    """
    Sum the values dictionnaries
    """

    for key in bipv_results_dict:
        if isinstance(bipv_results_dict[key], dict):
            bipv_results_dict[key] = compute_cumulative_and_total_value_bipv_result_dict(bipv_results_dict[key])
        elif isinstance(bipv_results_dict[key], list) and key == "yearly":
            bipv_results_dict["cumulative"] = [sum(bipv_results_dict["yearly"][0:i]) for i in range (1, len(bipv_results_dict["yearly"])+1)]
            bipv_results_dict["total"] = bipv_results_dict["cumulative"][-1]

    return bipv_results_dict

result = compute_cumulative_and_total_value_bipv_result_dict(result_dict3)
print(result)