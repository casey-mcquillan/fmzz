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
os.chdir(code_folder)

### Import calibration class
from fzz_calibration import calibration_model 


#%%  Importing Data #%%  
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%  Calibration Over Time #%% 
# Parameter assumptions:
alpha_c=1
alpha_n=1

# Outcomes to track
years = [1977,1987] + list(range(1996, 2019))
results_variables = ['Percent Reduction in College Wage Premium']
df_results = pd.DataFrame(columns=results_variables, index=years)

# Loop through and calibrate model each year
for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage_c'], 
                w1_n=df_observed.loc[year, 'wage_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                epop_ratio1=df_observed.loc[year, 'epop_ratio'],
                pop_count=df_observed.loc[year, 'pop_count'])
    
    #Make sure there are no NANs in model before calibration
    if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
        print("NAN value entered into calibration model for:")
        for var in vars(model).keys():
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))
        continue
    
    #Calibrate Model
    model.calibrate()
    
    #Collect relevant statistics
    college_wage_premium1 = (model.w1_c - model.w1_n)
    college_wage_premium2 = (model.w2_c - model.w2_n)
    y = (college_wage_premium2 - college_wage_premium1) / college_wage_premium1
    df_results.loc[year, 'Percent Reduction in College Wage Premium'] = y
    
    
#%%  Summary Table Over Time #%% 
# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables'
years = [1977,1987] + list(range(1996, 2019))
for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage_c'], 
                w1_n=df_observed.loc[year, 'wage_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                epop_ratio1=df_observed.loc[year, 'epop_ratio'],
                pop_count=df_observed.loc[year, 'pop_count'])


        #Make sure there are no NANs in model before calibration
    if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
        print("NAN value entered into calibration model for:")
        for var in vars(model).keys():
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))
        continue
    
    #Calibrate Model
    model.calibrate()
    
    #Generate LaTeX Summary Table
    model.generate_table(file_name='SummaryTable'+str(year), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year), 
                         location=output_path)
    
    model.generate_table(file_name='EqComparison'+str(year), year=year, 
                     table_type="equilibrium comparison", table_label="EqComparison"+str(year), 
                     location=output_path)
    
    
    