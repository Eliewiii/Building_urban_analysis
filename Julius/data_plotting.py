"""
Scripts to plot data from UBES and BIPV simulations

"""

import matplotlib.pyplot as plt
import numpy as np
import json

def kpi_bar(location, start_year, end_year):

    # Open and read the JSON file
    with open(location, 'r') as file:
        data_dict = json.load(file)
    # Data
    years = [i for i in range(start_year, end_year)]

    scenarios = [str(key) for key in data_dict["cigs"].keys()]  # Get scenario keys
    print(scenarios)
    eroi = [data_dict["cigs"][scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['kpis']['eroi']['total'] for scenario in
            scenarios]
    paybacktime_threshold = [
        data_dict["cigs"][scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['kpis']['economical payback time [year]'][
            'profitability_threshold']['total'] for scenario in scenarios]
    paybacktime_lifetime = [
        data_dict["cigs"][scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['kpis']['economical payback time [year]'][
            'lifetime_investment']['total'] for scenario in scenarios]
    roi = [data_dict["cigs"][scenario]["bipv_and_kpi_simulation"]['kpis_results_dict']['kpis']['economical roi']['total'] for scenario in
           scenarios]

    # Ensure all lists have the same length

    print(eroi)
    print(roi)
    print(paybacktime_lifetime)
    print(paybacktime_threshold)

    # Number of scenarios
    n = len(scenarios)
    index = np.arange(n)  # Array of scenario indices
    bar_width = 0.35  # Width of the bars

    # Create the figure and axes (2 subplots stacked vertically)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # First grouped bar chart (EROI and ROI)
    rects1 = ax1.bar(index, eroi, bar_width, label='EROI', color='blue')
    rects2 = ax1.bar(index + bar_width, roi, bar_width, label='ROI', color='green')

    # Customize the first chart
    ax1.set_xlabel('Scenarios')
    ax1.set_ylabel('EROI / ROI')
    ax1.set_title('EROI and ROI across Scenarios')
    ax1.set_xticks(index + bar_width / 2)
    ax1.set_xticklabels(scenarios, rotation=45)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.axhline(1, color='black', linewidth=1)

    # Second grouped bar chart (Economical and Environmental Payback Times)
    rects3 = ax2.bar(index, paybacktime_threshold, bar_width, label='Payback Time Threshold', color='orange')
    rects4 = ax2.bar(index + bar_width, paybacktime_lifetime, bar_width, label='Payback Time Lifetime', color='red')

    # Customize the second chart
    ax2.set_xlabel('Scenarios')
    ax2.set_ylabel('Payback Time (Years)')
    ax2.set_title('Economical and Environmental Payback Times across Scenarios')
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(scenarios, rotation=45)
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Adjust the layout to prevent overlap
    plt.tight_layout()

    # Show the plot
    plt.show()