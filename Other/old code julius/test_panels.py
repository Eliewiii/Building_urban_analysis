# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:06:46 2023

@author: juliu
"""
from functions_dmfa_cur import *
from functions_energy_cur import *

panels = [23, 46, 69, 78, 104]
energy_list = []

# setting start and endyear for calculating energy efficiency    
for index in range(len(panels)):
    if index == 0:
        start = 1
        stop = panels[index]
    elif index == len(panels) -1 :
        start = panels[-2]
        stop = 101
    else:
        start = panels[index - 1]
        stop = panels[index]
        
    print(start, stop)
    
# calculating energy efficiency year by year through annual degradation   
    for year in range(start, stop):
        
        if index == 0:
            age = year
            installation_year = 0
            
        elif index != 0:
            age = year - panels[index - 1]
            installation_year = panels[index - 1]
            
        deg = calc_degradation(age)
        energy_provision = energy_efficiency["efficient"]["rooftech"][installation_year] * (1 - deg)
        print(year, panels[index], age, deg)
        print(energy_efficiency["efficient"]["rooftech"][installation_year], energy_provision)

        energy_list.append(energy_provision)

print(energy_list)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(list_life[:], energy_list, color = "k")
ax.set_xlabel('Years')
ax.set_ylabel('Energy efficiency', color='k')
plt.rcParams.update({'font.size': 14})
plt.legend(loc="upper left")
plt.show