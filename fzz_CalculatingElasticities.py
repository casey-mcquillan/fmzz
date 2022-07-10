#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 19:21:05 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]

#Define Model
model = calibration_model(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c=df_observed.loc[year, 'wage1_c'], 
                    w1_n=df_observed.loc[year, 'wage1_n'],
                    P1_c=df_observed.loc[year, 'P1_c'], 
                    P1_n=df_observed.loc[year, 'P1_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    pop_count=df_observed.loc[year, 'pop_count'])

#Make sure there are no NANs in model before calibration
# Remove elasticities if specified to be common
if model.elasticity_c == model.elasticity_n == 'common': 
    check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
else: check = vars(model).keys()
#And now check
if any(np.isnan([vars(model)[x] for x in check])):
    print("NAN value entered into calibration model for:")
    for var in check:
        if np.isnan(vars(model)[var])==True: print("    "+var)
    print("for year: " + str(year))

#Calibrate Model
model.calibrate()



#%%      Calculating Labor Supply Elasticity:      %%#

elasticity_S_n = model.kappa_dist_n**(-1) * model.w1_n * model.P1_n**(-1)
elasticity_S_c = model.kappa_dist_c**(-1) * model.w1_c * model.P1_c**(-1)



#%%      Calculating Labor Demand Elasticity:      %%#

## For brevity, save these values
rho = model.rho
tau = model.tau
lambda_n = model.lambda_n
lambda_c = model.lambda_c
w_n = model.w1_n
w_c = model.w1_c
L_n = model.L1_n
L_c = model.L1_c

## Non-College
term1 = -1/(1-rho)
term2 = lambda_c**(1/rho) * L_c
term3 = (((w_n+tau)/lambda_n)**(rho/(1-rho)) - lambda_n)**((-1-rho)/rho)
term4 = (w_n+tau)**((2*rho-1)/(1-rho))
term5 = lambda_n**(-1*rho/(1-rho))
term6 = (w_n / L_n)

elasticity_D_n = term1*term2*term3*term4*term5*term6


## College
term1 = -1/(1-rho)
term2 = lambda_n**(1/rho) * L_n
term3 = (((w_c+tau)/lambda_c)**(rho/(1-rho)) - lambda_c)**((-1-rho)/rho)
term4 = (w_c+tau)**((2*rho-1)/(1-rho))
term5 = lambda_c**(-1*rho/(1-rho))
term6 = (w_c / L_c)

elasticity_D_c = term1*term2*term3*term4*term5*term6


