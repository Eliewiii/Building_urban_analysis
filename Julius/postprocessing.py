"""
processing the results from the UBES and BIPV simulation, including discounting, carbon credit

"""

def calculate_npv_per_year(cash_flows, discount_rate):
    """
    Calculate the Net Present Value (NPV) for each year of an investment and returns a two lists: one cumulative, one yearly.

    Parameters:
    - cash_flows (list of float): List of yearly cash flows including the initial investment.
    - discount_rate (float): The discount rate as a decimal (e.g., 0.1 for 10%).

    Returns:
    - npv_list (list of float): A list of NPV values, one for each year.
    """
    npv_list_cumu = []
    npv_list_yearly = []

    cumulative_npv = cash_flows[0]  # Start with the initial investment (year 0, no discount)
    npv_list_cumu.append(cumulative_npv)
    npv_list_yearly.append(cash_flows[0])

    # Calculate NPV for each year after the initial investment
    for t, cash_flow in enumerate(cash_flows[1:], start=1):
        yearly_npv = cash_flow / (1 + discount_rate) ** t
        cumulative_npv += yearly_npv
        npv_list_cumu.append(cumulative_npv)
        npv_list_yearly.append(yearly_npv)

    return npv_list_cumu, npv_list_yearly


def include_carbon_credit(carbon_credit, ghg_emissions, scenario, data_dict):
    """
    Add on a revenue from carbon credits for each kWh of produced energy.

    Parameters:
    - carbon credit rate in USD/kWh
    - ghg_emissions: emissions per kWh
    - scenario that is processed
    - data_dict: dictionary with stored results

    Returns:
    - npv_list (list of float): A list of NPV values, one for each year.
    """


    # revenues without carbon credit
    revenue_list = [data_dict[scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total']['net_economical_income']['yearly'][i] for i in range(0,50)]
    benefit_list = [data_dict[scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['intermediate_results']['total']['net_economical_benefit']['yearly'][i] for i in range(0,50)]
    list_revenue_with_cc = []
    list_benefit_with_cc = []

    for i in range(0,len(revenue_list)):

        list_revenue_with_cc.append(revenue_list[i] + carbon_credit * ghg_emissions *
                                    data_dict[scenario]["bipv_and_kpi_simulation"]['bipv_results_dict']['total']['energy_harvested']['yearly'][i] /
                                    1000)

        # update net_economical_benefit with new revenue list to include carbon credit
        list_benefit_with_cc.append(benefit_list[i] + carbon_credit * ghg_emissions *
                                data_dict[scenario]["bipv_and_kpi_simulation"]['bipv_results_dict']['total']['energy_harvested']['yearly'][i] /
                                   1000)


    return list_revenue_with_cc, list_benefit_with_cc

