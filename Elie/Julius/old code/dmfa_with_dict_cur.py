# -*- coding: utf-8 -*-
"""     
Created on Mon Jan  2 09:28:46 2023

@author: Julius Jandl
*STOCK DRIVEN DYNAMIC MFA MODEL FOR PV WASTE*

This code is providing an age-cohort based model to calculate emerging PV-Waste from a constant stock using the Weibull distribution.
"""

""" 
Imports:
"""
from functions_dmfa_cur import *
from functions_energy_cur import *
from functions_lca_cur import *


# setup of inputs
wb_cumu_RL = calc_wb_cumu(nb_of_years, lt_PV, wb_shape_RL)
wb_cumu_EL = calc_wb_cumu(nb_of_years, lt_PV, wb_shape_EL)
dic_wb = {"regular loss": wb_cumu_RL, "early loss" : wb_cumu_EL}

nb_of_years = 100
list_b_type = [area_file.cell(i, 3).value for i in range(4,5)]
list_scenario = ["roof_scenario", "env_scenario"]
list_tech = ["rooftech", "envtech"]
list_wb = ["regular loss", "early loss"]

dic_result_per_year = {}
dic_energy = {}
dic_impact = {}

#INPUTS
wb = "regular loss" #regular loss or early loss
level = "efficient" # efficient or aesthetic
construction = "simple" # simple or phased

data, data_real = create_data(level, wb, construction)
energy_data = run_energy(dic_energy, data, wb, level, construction)
impact_data = run_lca(dic_impact, data)

# data will be written to excel files
# write_energy_data(energy_data, wb, level, nb_of_years)            
# write_waste_data(data, data_real, "ideal", wb, level, nb_of_years)

