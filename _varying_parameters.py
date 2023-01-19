#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 22:35:07 2023
@author: caseymcquillan
"""
# varying tau
tau_params = ['tau_baseline', 'tau_fullcoverage']
tau2specification_Dict ={'tau_baseline':'Total Cost with Incomplete Takeup',
                         'tau_fullcoverage':'Total Cost with Complete Takeup'}

# varying elasticitiy parameters
elasticity_values = ['implied', [0.15,0.15],[0.3,0.3],[0.45,0.45]]
elasticity2specification_Dict ={'implied':'Common $\kappa$',
                         str([0.15,0.15]): 'Low (0.15)',
                         str([0.3,0.3]): 'Medium (0.30)',
                         str([0.45,0.45]): 'High (0.45)'}

# varying rho parameters
rho_values = [1, 0.3827, 0.01]
rho2specification_Dict ={str(1):'Perfect Substitutes',
                         str(0.3827): 'Gross Substitutes',
                         str(0.01): 'Cobb-Douglas'}

'''
#Parameter(s) to be varied
from _varying_parameters import tau_params, tau2specification_Dict
from _varying_parameters import elasticity_values, elasticity2specification_Dict
from _varying_parameters import rho_values, rho2specification_Dict
'''