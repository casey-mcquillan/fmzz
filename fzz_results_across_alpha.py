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
year = 2018
tau_param = 'tau_high'
alpha_values = [[1,1], [1.2,1.2], [0.8,0.8], [0.9,0.7]]

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Different Alpha'

#Create list for table values specific to each value of tau
comparison_table_values = []

#Loop through values of tau
for alphas in alpha_values:    
    case_num = alpha_values.index(alphas)    
    alpha_c, alpha_n, = alphas[0], alphas[1]
    
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, tau_param], 
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
    model.generate_table(file_name='SummaryTable'+str(year)+"_alpha"+str(case_num), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year)+"-alpha"+str(case_num), 
                         location=output_path)
    
    model.generate_table(file_name='EqComparison'+str(year)+"_alpha"+str(case_num), year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"-alpha"+str(case_num), 
                     location=output_path)
    
    #Create list with comparison table values for this section
    table_values_section = [f'\\underline{{ \\alpha_C = {alpha_c}, \\alpha_N = {alpha_n} }} \\\\', '\n',
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
header = [f'\ctable[caption={{Calibration Results Across $\\alpha$ for {year} }},', '\n',
        f'    label=ResultsAcrossAlpha{year}, pos=h!]', '\n',
        '{lcc}{}{\\FL', '\n',
        '&  \\small (No ESHI $\\Rightarrow$ Head Tax)', '\n',
        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
        '\\cmidrule{1-3}', '\n']

closer = ['\\bottomrule}']

cwd = os.getcwd()
os.chdir(output_path)
file = open("Results_across_alpha_"+str(year)+".tex","w")
file.writelines(header) 
file.writelines(comparison_table_values)   
file.writelines(closer)   
file.close()
os.chdir(cwd)
    