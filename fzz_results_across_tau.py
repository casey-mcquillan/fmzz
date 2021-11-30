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
alpha_c=1
alpha_n=1
year = 2019

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Different Tau'


#Set up params and file for comparison table
tau_params = ['tau_high', 'tau_med', 'tau_low']
tau2specification_Dict ={'tau_high':'Total Cost and Complete Take-up',
                         'tau_med':'Cost to Employer and Complete Take-up',
                         'tau_low':'Cost to Employer and Incomplete Take-up'}

#Create list for table values specific to each value of tau
comparison_table_values = []

#Loop through values of tau
for tau_param in tau_params:
    
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
    model.generate_table(file_name='SummaryTable'+str(year)+"_"+str(tau_param), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year)+"_"+str(tau_param), 
                         location=output_path)
    
    model.generate_table(file_name='EqComparison'+str(year)+"_"+str(tau_param), year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"_"+str(tau_param), 
                     location=output_path)
    
    #Create list with comparison table values for this section
    table_values_section = [f'\\underline{{ {tau2specification_Dict[tau_param]} }} \\\\', '\n',
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
header = [f'\ctable[caption={{Calibration Results Across $\\tau$ with $\\alpha_C = {alpha_c}, \\alpha_N = {alpha_n}$}} for {year},', '\n',
        f'    label=ResultsAcrossTau{year}, pos=h!]', '\n',
        '{lcc}{',
            '$^{*}$& The values of $\\tau$: ',  '\n',
            f'    (1) Total Cost and Complete Take-up: \\${df_observed.loc[year, tau_params[0]]:,.0f}; ',  '\n',
            f'    (2) Cost to Employer and Complete Take-up: \\${df_observed.loc[year, tau_params[1]]:,.0f}; ',  '\n',
            f'    (3) Cost to Employer and Incomplete Take-up: \\${df_observed.loc[year, tau_params[2]]:,.0f}. \\N',  '\n',
        '}{\\FL', '\n',
        '&  \\small (No ESHI $\\Rightarrow$ Head Tax)', '\n',
        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
        '\\cmidrule{1-3}', '\n']

closer = ['\\bottomrule}']

cwd = os.getcwd()
os.chdir(output_path)
file = open("Results_across_tau_"+str(year)+".tex","w")
file.writelines(header) 
file.writelines(comparison_table_values)   
file.writelines(closer)   
file.close()
os.chdir(cwd)
    