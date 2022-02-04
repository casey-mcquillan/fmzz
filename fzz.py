#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 23:09:14 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_path_Baseline = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Baseline'
output_path_SummaryTable = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/SummaryTable_byYear'
output_path_EqComparison = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/EqComparison_byYear'

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model 


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)
df_observed_RC1 = pd.read_csv('observed_data_RC1.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year = 2019

#Baseline Parameters
tau_baseline = 'tau_high'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Baseline Estimate      %%#
#Results for Overview Table
baselines_results_string = []

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

#Generate LaTeX Summary Table
model.generate_table(file_name='SummaryTable'+str(year)+"_baseline", year=year, 
                     table_type="equilibrium summary", 
                     table_label="SummaryTable"+str(year)+"baseline", 
                     location=output_path_Baseline, subtitle=f' with Baseline Parameters')

model.generate_table(file_name='EqComparison'+str(year)+"_baseline", year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"_baseline", 
                     location=output_path_Baseline, subtitle=f' with Baseline Parameters')
    
    
#%%      Summayr Table and Equilibrium Comparison by Year     %%#
# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables'
years = [1977,1987] + list(range(1996, 2020))
P1_c= pd.DataFrame(index=years)
P1_n= pd.DataFrame(index=years)
for year in years:
    
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

    
    #Generate LaTeX Summary Table
    model.generate_table(file_name='SummaryTable'+str(year), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year), 
                         location=output_path_EqComparison)
    
    model.generate_table(file_name='EqComparison'+str(year), year=year, 
                     table_type="equilibrium comparison", table_label="EqComparison"+str(year), 
                     location=output_path_SummaryTable)