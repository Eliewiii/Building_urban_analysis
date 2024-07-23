"""
Database for the design variables and their boundaries.
All possible design variables and their boundaries are defined here.
They can be imported in the optimization scripts to define the search space.
The DV suffix stands for Design Variable.
"""

import nevergrad as ng

###############################
# Float design variables
###############################

# Inverter sizing ratios
roof_inverter_sizing_ratio_dv = ng.p.Scalar(
    lower=0.70,
    upper=1.
)
facades_inverter_sizing_ratio_dv = ng.p.Scalar(
    lower=0.60,
    upper=1.
)

# Minimum Panel EROI
min_panel_eroi_dv = ng.p.Scalar(
    lower=1.2,
    upper=3.0
)

###############################
# Integer design variables
###############################

# Panel Replacement frequency
""" The replacement frequency will be multiplied by 5"""
replacement_frequency_dv = ng.p.Scalar(
    lower=1,
    upper=8
).set_integer_casting()

REPLACEMENT_FREQUENCY_MULTIPLIER = 5

###############################
# Categorial design variables
###############################

# Roof Panel technology ids
ROOF_PANEL_TECHNOLOGIES_DICT = {
    0: 'mitrex_facades c-Si Solar Siding 350W - Dove Grey china default',
    1: 'mitrex_roof c-Si M390-A1F default'
}
ROOF_PANEL_TECHNOLOGIES_REVERT_DICT= {v: k for k, v in ROOF_PANEL_TECHNOLOGIES_DICT.items()}
roof_panel_id_dv = ng.p.Choice(range(len(ROOF_PANEL_TECHNOLOGIES_DICT.keys())))

# Facades Panel technology ids
FACADES_PANEL_TECHNOLOGIES_DICT = {
    0: 'mitrex_facades c-Si Solar Siding 350W - Dove Grey china default',
    1: 'mitrex_roof c-Si M390-A1F default'
}
FACADES_PANEL_TECHNOLOGIES_REVERT_DICT= {v: k for k, v in FACADES_PANEL_TECHNOLOGIES_DICT.items()}
facades_panel_id_dv = ng.p.Choice(range(len(FACADES_PANEL_TECHNOLOGIES_DICT.keys())))
