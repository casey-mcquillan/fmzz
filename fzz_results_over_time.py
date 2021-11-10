#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 18:37:37 2021

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
year_values = [2017, 2007, 1997, 1987, 1977]
tau_param = 'tau_high'
alpha_c, alpha_n, = 1, 1

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Over Time'

#Create list for table values specific to each value of tau
comparison_table_values = []

#Loop through values of tau
for year in year_values:    
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, tau_param], 
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
                         location=output_path)
    
    model.generate_table(file_name='EqComparison'+str(year), year=year, 
                         table_type="equilibrium comparison", 
                         table_label="EqComparison"+str(year), 
                         location=output_path)
    
    #Create list with comparison table values for this section
    table_values_section = [f'\\underline{{ Calibration for {year} }} \\\\', '\n',
    f'\\ \\ \\small Pct. Chg. in College Wage Premium',
        f' & {100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n):,.2f}\\%',
        f' & {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\%',
        ' \\\\\n',
    f'\\ \\ \\small Change in College Share of Wage Bill', 
        f' & {100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))-((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n))):,.2f} pp',
        f' & {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp',
        ' \\\\\n',
        '\\\\\n']
    #Append this to the existing list
    comparison_table_values.extend(table_values_section)


#Generate header and close 
header = [f'\ctable[caption={{Calibration Results over Time with $\\alpha_C =\\alpha_N = 1$  }},', '\n',
        f'    label=ResultsOverTime, pos=h!]', '\n',
        '{lcc}{', '\n',
        '$^{*}$& These calibrations use the value of $\\tau$ based on the total cost with complete take-up.',  '\n',
        '}{\\FL', '\n',
        '&  \\small (No ESHI $\\Rightarrow$ Head Tax)', '\n',
        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
        '\\cmidrule{1-3}', '\n']

closer = ['\\bottomrule}']

cwd = os.getcwd()
os.chdir(output_path)
file = open("Results_over_time.tex","w")
file.writelines(header) 
file.writelines(comparison_table_values)   
file.writelines(closer)   
file.close()
os.chdir(cwd)
    