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


###############################
# Integer design variables
###############################

# Minimum Panel EROI
min_panel_eroi_dv = ng.p.Scalar(
    lower=0,
    upper=10
).set_integer_casting()

# Panel Replacement frequency
""" The replacement frequency will be multiplied by 5"""
replacement_frequency_dv = ng.p.Scalar(
    lower=1,
    upper=8
).set_integer_casting()


###############################
# Categorial design variables
###############################

# Roof Panel techonology ids
ROOF_PANEL_TECHNOLOGIES = ['A', 'B']
roof_panel_id_dv = ng.p.Choice(range(len(ROOF_PANEL_TECHNOLOGIES)))

# Facades Panel techonology ids
FACADES_PANEL_TECHNOLOGIES = ['C', 'D']
facades_panel_id_dv = ng.p.Choice(range(len(FACADES_PANEL_TECHNOLOGIES)))
