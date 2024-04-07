"""Parameters of the Electricity Grid for the KPIs computation.
The default values
    Inputs:
        _grid_ghg_intensity: Green house gaz intensity of the electricity grid in kgCO2/kWh.
        _grid_energy_intensity: Energy intensity of the electricity grid in kWh/kWh.
        _grid_electricity_sell_price: Sell price of the electricity in $/kWh.
    Output:
        electricity_grid_parameters: Dictionary containing the electricity grid parameters"""

__author__ = "elie-medioni"
__version__ = "2024.03.31"

ghenv.Component.Name = "BUA Electricity Grid Parameters"
ghenv.Component.NickName = 'ElectricityGridParameters'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import json

# Initialize the replacement scenario parameter dictionary
electricity_grid_parameters_dict = {
    "grid_ghg_intensity": None,
    "grid_energy_intensity": None,
    "grid_electricity_sell_price": None
}

# Check the _grid_ghg_intensity
if _grid_ghg_intensity is not None:
    if _grid_ghg_intensity <= 0:
        raise ValueError("The Green House Gaz intensity of the electricity grid must be a positive number.")
    else:
        electricity_grid_parameters_dict["grid_ghg_intensity"] = _grid_ghg_intensity
# Check the _grid_energy_intensity
if _grid_energy_intensity is not None:
    if _grid_energy_intensity <= 0:
        raise ValueError("The energy intensity of the electricity grid must be a positive number.")
    else:
        electricity_grid_parameters_dict["grid_energy_intensity"] = _grid_energy_intensity
# Check the _grid_electricity_sell_price
if _grid_electricity_sell_price is not None:
    if _grid_electricity_sell_price <= 0:
        raise ValueError("The sell price of the electricity must be a positive number.")
    else:
        electricity_grid_parameters_dict["grid_electricity_sell_price"] = _grid_electricity_sell_price

electricity_grid_parameters = json.dumps(electricity_grid_parameters_dict)
