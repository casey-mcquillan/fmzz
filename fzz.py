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


#%%  Baseline Case #%% 
# Parameter assumptions:
alpha_c=1
alpha_n=1

# Outcomes to track
year = 2018

#Define and calibrate model
model = calibration_model(alpha_c, alpha_n,
            tau=df_observed.loc[year, 'tau_high'], 
            w1_c=df_observed.loc[year, 'wage1_c'], 
            w1_n=df_observed.loc[year, 'wage1_n'],
            P1_c=df_observed.loc[year, 'P1_c'], 
            P1_n=df_observed.loc[year, 'P1_n'],
            share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
            share_pop_c=df_observed.loc[year, 'share_pop_c'],
            pop_count=df_observed.loc[year, 'pop_count'])

#Make sure there are no NANs in model before calibration
if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
    print("NAN value entered into calibration model for:")
    for var in vars(model).keys():
        if np.isnan(vars(model)[var])==True: print("    "+var)
    print("for year: " + str(year))

#Calibrate Model
model.calibrate()

#Output LaTeX Tables
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Baseline'
model.generate_table(file_name='SummaryTable'+str(year)+"_baseline", year=year, 
                     table_type="equilibrium summary", 
                     table_label="SummaryTable"+str(year)+"_baseline", 
                     location=output_path)

model.generate_table(file_name='EqComparison'+str(year)+"_baseline", year=year, 
                 table_type="equilibrium comparison", 
                 table_label="EqComparison"+str(year)+"_baseline", 
                 location=output_path)
    
    
#%%  Summary Table Over Time #%% 
# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years

output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables'
years = [1977,1987] + list(range(1996, 2019))
P1_c= pd.DataFrame(index=years)
P1_n= pd.DataFrame(index=years)
for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
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
                         location=output_path+'/EqComparison_byYear')
    
    model.generate_table(file_name='EqComparison'+str(year), year=year, 
                     table_type="equilibrium comparison", table_label="EqComparison"+str(year), 
                     location=output_path+'/SummaryTable_byYear')