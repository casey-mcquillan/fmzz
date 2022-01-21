#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 14:39:40 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/ZidarOverview'

### Import calibration class
os.chdir(code_folder)

#from fzz_calibration import calibration_model 
from fzz_calibration_RC4_zwick import calibration_model_RC4 


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
model = calibration_model_RC4(alpha_c, alpha_n,
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
                     location=output_path, subtitle=f' with Baseline Parameters')

model.generate_table(file_name='EqComparison'+str(year)+"_baseline", year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"_baseline", 
                     location=output_path, subtitle=f' with Baseline Parameters')

#Save Results for Overview
pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                   -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
pp_chg_P_N = 100*(model.P2_n - model.P1_n)
baselines_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & {pp_chg_cwb:,.2f} pp & {pp_chg_P_N:,.2f} pp \\\\ ')

#%%      Vary Tau:      %%#
#Results for Overview Table
tau_results_string = []

#Parameters to be varied:
tau_params = ['tau_high', 'tau_med', 'tau_low']
tau2specification_Dict ={'tau_high':'Total Cost with Complete Take-up',
                         'tau_med':'Cost to Employer with Complete Take-up',
                         'tau_low':'Cost to Employer with Incomplete Take-up'}

#Initialize strings for tables
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
delta_cwg_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
pct_chg_cwg_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'

#Loop through
i = 0
for tau_param in tau_params:
    i = i+1
    label = tau2specification_Dict[tau_param]
    
    #Define Model
    model = calibration_model_RC4(alpha_c, alpha_n,
                        rho=rho_baseline,
                        tau=df_observed.loc[year, tau_param],
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
    model.generate_table(file_name='SummaryTable'+str(year)+'_'+tau_param, year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year)+tau_param, 
                         location=output_path, subtitle=f' using {label}')
    
    #Save Results for Overview
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                       -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    tau_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & {pp_chg_cwb:,.2f} pp & {pp_chg_P_N:,.2f} pp \\\\ ')
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    delta_cwg_string = delta_cwg_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
    pct_chg_cwg_string = pct_chg_cwg_string + ampersand + \
        f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    pct_chg_L_string = pct_chg_L_string + ampersand +  \
        f' {100*((model.L2_c+model.L2_n)-(model.L1_c+model.L1_n))/(model.L1_c+model.L1_n):,.2f}\\% '
    pct_chg_L_C_string = pct_chg_L_C_string + ampersand + \
        f' {100*((model.L2_c)-(model.L1_c))/(model.L1_c):,.2f}\\% '
    pct_chg_L_B_string = pct_chg_L_B_string + ampersand + \
        f' {100*((model.L2_n)-(model.L1_n))/(model.L1_n):,.2f}\\% '
    
    delta_employmentShare_C_string = delta_employmentShare_C_string + ampersand + \
        f' {100*(((model.L2_c)/(model.L2_c+model.L2_n))-((model.L1_c)/(model.L1_c+model.L1_n))):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'
    
header = [f'\ctable[caption={{Equilibrium Comparison Across ESHI Cost Assumptions}},', '\n',
          '    label={EqComparison_AcrossTau}, pos=h!]', '\n',
          '{lccccc}{}{\\FL', '\n',
          '\t &	 \small \multicolumn{1}{p{3cm}}{\centering Total Cost, \\ Complete Take-up}','\n', 
          '\t &&	 \small \multicolumn{1}{p{3cm}}{\centering  Cost to Employer, \\ Complete Take-up}','\n', 
          '\t &&	 \small \multicolumn{1}{p{3cm}}{\centering Cost to Employer, \\ Incomplete Takeup}', '\\\\','\n', 
          '\cmidrule{1-6}', '\n']

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                delta_cwg_string, ' \\\\\n',
                pct_chg_cwg_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Labor Supply:}', ' \\\\\n',
                pct_chg_L_string, ' \\\\\n',
                pct_chg_L_C_string, ' \\\\\n',
                pct_chg_L_B_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_employmentShare_C_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("EqComparison_AcrossTau.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()


#%%      Vary Elasticties:      %%#
#Results for Overview Table
elasticity_results_string = []

# Parameter to be varied:
elasticity_values = [['common','common'], [0.15,0.15],[0.3,0.3],[0.45,0.45]]
elasticity2specification_Dict ={str(['common','common']):'Common $\kappa$',
                         str([0.15,0.15]): 'Low (0.15)',
                         str([0.3,0.3]): 'Medium (0.30)',
                         str([0.45,0.45]): 'High (0.45)'}

#Initialize strings for tables
column_header_string = '$(\epsilon^H_C, \epsilon^H_N)$ '
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
delta_cwg_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
pct_chg_cwg_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'


# Loop through elasticity pairs in calibration process
i = 0
for elasticity_value in elasticity_values:
    i = i+1
    e_c, e_n, = elasticity_value[0], elasticity_value[1]
    label = elasticity2specification_Dict[str(elasticity_value)]
    
    #Define and calibrate model
    model = calibration_model_RC4(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year, tau_baseline],
                elasticity_c=e_c, elasticity_n=e_n,
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                pop_count=df_observed.loc[year, 'pop_count'])
    
    #Make sure there are no NANs in model before calibration
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
    
    #Output Summary tables
    model.generate_table(file_name='SummaryTable'+str(year)+f"_elasticity{i}", year=year, 
                     table_type="equilibrium summary",
                     table_label="SummaryTable"+str(year)+f"__elasticity{i}", 
                     location=output_path, 
                     subtitle=f" with {label} Elasticity")

    #Save Results for Overview
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                       -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    elasticity_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & {pp_chg_cwb:,.2f} pp & {pp_chg_P_N:,.2f} pp \\\\ ')

    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    delta_cwg_string = delta_cwg_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
    pct_chg_cwg_string = pct_chg_cwg_string + ampersand + \
        f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    pct_chg_L_string = pct_chg_L_string + ampersand +  \
        f' {100*((model.L2_c+model.L2_n)-(model.L1_c+model.L1_n))/(model.L1_c+model.L1_n):,.2f}\\% '
    pct_chg_L_C_string = pct_chg_L_C_string + ampersand + \
        f' {100*((model.L2_c)-(model.L1_c))/(model.L1_c):,.2f}\\% '
    pct_chg_L_B_string = pct_chg_L_B_string + ampersand + \
        f' {100*((model.L2_n)-(model.L1_n))/(model.L1_n):,.2f}\\% '
    
    delta_employmentShare_C_string = delta_employmentShare_C_string + ampersand + \
        f' {100*(((model.L2_c)/(model.L2_c+model.L2_n))-((model.L1_c)/(model.L1_c+model.L1_n))):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'
    
header = [f'\ctable[caption={{Equilibrium Comparison Across Elasticity Assumptions}},', '\n',
          '    label={EqComparison_AcrossElasticity}, pos=h!]', '\n',
          '{lccccccc}{}{\\FL', '\n',
          column_header_string, '\\\\',
          '\cmidrule{1-8}', '\n']            

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                delta_cwg_string, ' \\\\\n',
                pct_chg_cwg_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Labor Supply:}', ' \\\\\n',
                pct_chg_L_string, ' \\\\\n',
                pct_chg_L_C_string, ' \\\\\n',
                pct_chg_L_B_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_employmentShare_C_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("EqComparison_AcrossElasticity.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()



#%%      Vary Substitutabilitity:      %%#
#Results for Overview Table
rho_results_string = []

# Parameter to be varied:
rho_values = [1, 0.3827, 0.01]
rho2specification_Dict ={str(1):'Perfect Substitutes',
                         str(0.3827): 'Gross Substitutes',
                         str(0.01): 'Cobb-Douglas'}

#Initialize strings for tables
column_header_string = ''
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
delta_cwg_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
pct_chg_cwg_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'


# Loop through rho values in calibration process
i = 0
for rho_value in rho_values:
    i = i+1
    label = rho2specification_Dict[str(rho_value)]
    
    #Define and calibrate model    
    model = calibration_model_RC4(alpha_c, alpha_n,
                rho=rho_value,
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
    
    #Output Summary tables
    model.generate_table(file_name='SummaryTable'+str(year)+f"_rho{i}", year=year, 
                     table_type="equilibrium summary",
                     table_label="SummaryTable"+str(year)+f"-rho{i}", 
                     location=output_path, 
                     subtitle=f" with {label}$")
    
    #Save Results for Overview
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                       -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    rho_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & {pp_chg_cwb:,.2f} pp & {pp_chg_P_N:,.2f} pp \\\\ ')
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    delta_cwg_string = delta_cwg_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
    pct_chg_cwg_string = pct_chg_cwg_string + ampersand + \
        f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    pct_chg_L_string = pct_chg_L_string + ampersand +  \
        f' {100*((model.L2_c+model.L2_n)-(model.L1_c+model.L1_n))/(model.L1_c+model.L1_n):,.2f}\\% '
    pct_chg_L_C_string = pct_chg_L_C_string + ampersand + \
        f' {100*((model.L2_c)-(model.L1_c))/(model.L1_c):,.2f}\\% '
    pct_chg_L_B_string = pct_chg_L_B_string + ampersand + \
        f' {100*((model.L2_n)-(model.L1_n))/(model.L1_n):,.2f}\\% '
    
    delta_employmentShare_C_string = delta_employmentShare_C_string + ampersand + \
        f' {100*(((model.L2_c)/(model.L2_c+model.L2_n))-((model.L1_c)/(model.L1_c+model.L1_n))):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'

header = [f'\ctable[caption={{Equilibrium Comparison Across Substitutability ($\\rho$) }},', '\n',
          '    label={EqComparison_AcrossRho}, pos=h!]', '\n',
          '{lccccc}{}{\\FL', '\n',
          column_header_string, '\\\\',
          '\cmidrule{1-6}', '\n']            

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                delta_cwg_string, ' \\\\\n',
                pct_chg_cwg_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Labor Supply:}', ' \\\\\n',
                pct_chg_L_string, ' \\\\\n',
                pct_chg_L_C_string, ' \\\\\n',
                pct_chg_L_B_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_employmentShare_C_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("EqComparison_AcrossRho.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()

#%%      Vary College Definition:      %%#
#Results for Overview Table
collegeDef_results_string = []

#Parameter to be varies
college_defs = [1, 2, 3]
college_defs2specification_Dict ={1:'Bachelor\s Degree or Higher',
                         2:'Associate\'s Degree or Higher',
                         3:'Some College or More'}

#Initialize strings for tables
column_header_string = ''
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
delta_cwg_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
pct_chg_cwg_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'

#Loop through vcollege definitions
i = 0
for def_num in [1,2,3]:  
    i = i+1 
    label = college_defs2specification_Dict[def_num]
    
    #Define and calibrate model
    model = calibration_model_RC4(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_c_baseline,
                w1_c=df_observed_RC1.loc[year, f'wage1_c [college definition {def_num}]'], 
                w1_n=df_observed_RC1.loc[year, f'wage1_n [college definition {def_num}]'],
                P1_c=df_observed_RC1.loc[year, f'P1_c [college definition {def_num}]'], 
                P1_n=df_observed_RC1.loc[year, f'P1_n [college definition {def_num}]'],
                share_workers1_c=df_observed_RC1.loc[year, f'share_workers1_c [college definition {def_num}]'],
                share_pop_c=df_observed_RC1.loc[year, f'share_pop_c [college definition {def_num}]'],
                pop_count=df_observed_RC1.loc[year, 'pop_count'])

    #Make sure there are no NANs in model before calibration
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
    model.generate_table(file_name='SummaryTable'+str(year)+"_college"+str(def_num), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year)+"college"+str(def_num), 
                         location=output_path, subtitle=f' with College Definition {def_num}')
    
    #Save Results for Overview
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                       -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    collegeDef_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & {pp_chg_cwb:,.2f} pp & {pp_chg_P_N:,.2f} pp \\\\ ')
    
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    delta_cwg_string = delta_cwg_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
    pct_chg_cwg_string = pct_chg_cwg_string + ampersand + \
        f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    pct_chg_L_string = pct_chg_L_string + ampersand +  \
        f' {100*((model.L2_c+model.L2_n)-(model.L1_c+model.L1_n))/(model.L1_c+model.L1_n):,.2f}\\% '
    pct_chg_L_C_string = pct_chg_L_C_string + ampersand + \
        f' {100*((model.L2_c)-(model.L1_c))/(model.L1_c):,.2f}\\% '
    pct_chg_L_B_string = pct_chg_L_B_string + ampersand + \
        f' {100*((model.L2_n)-(model.L1_n))/(model.L1_n):,.2f}\\% '
    
    delta_employmentShare_C_string = delta_employmentShare_C_string + ampersand + \
        f' {100*(((model.L2_c)/(model.L2_c+model.L2_n))-((model.L1_c)/(model.L1_c+model.L1_n))):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'

       
header = [f'\ctable[caption={{Equilibrium Comparison for {year} Across College Definitions}},', '\n',
          '    label={EqComparison_AcrossCollegeDef}, pos=h!]', '\n',
          '{lccccc}{}{\\FL', '\n',
          '\t &	 \small \multicolumn{1}{p{3cm}}{\centering Bachelor\'s Degree \\\\ or Higher}','\n', 
          '\t &&	 \small \multicolumn{1}{p{3cm}}{\centering  Associate\'s Degree \\\\ or Higher}','\n', 
          '\t &&	 \small \multicolumn{1}{p{3cm}}{\centering Some College \\\\ or More}', '\\\\', '\n', 
          '\cmidrule{1-6}', '\n']

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                delta_cwg_string, ' \\\\\n',
                pct_chg_cwg_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Labor Supply:}', ' \\\\\n',
                pct_chg_L_string, ' \\\\\n',
                pct_chg_L_C_string, ' \\\\\n',
                pct_chg_L_B_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_employmentShare_C_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("EqComparison_AcrossCollegeDef.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()


#%%      Compile Overview Tables:      %%#
header = ['\ctable[caption={Summary of Results Across Specifications},', ' \n',
            '    label={SummaryOverview}, pos=h!]', ' \n',
            '{lccc}{}{\\FL', '\n',
            '\t &    \small \multicolumn{1}{p{3cm}}{\centering Pct. Chg. College \\\\ Wage Premium}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3cm}}{\centering  PP. Chg. College \\\\ Wage Bill}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3.5cm}}{\centering PP. Chg. Non-College \\\\ Employment Rate}', '\\\\', '\n',
            '\cmidrule{1-4}', '\n',
            '\\\\' '\n']  

baseline = [r'\underline{Baseline:}', ' \n', 
          baselines_results_string[0], ' \n',
          '\\\\', ' \n'] 

acrossTau = [r'\underline{Cost of ESHI:} \\', ' \n ',
    '\ \ \small \shortstack[l]{Total Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string[0], ' \n',
    '\ \ \small \shortstack[l]{Employer Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string[1], ' \n',
    '\ \ \small \shortstack[l]{Employer Cost with \\\\ \ \ Complete Take-up}',
    ' \n', tau_results_string[2], ' \n',
    '\\\\', ' \n ',] 

acrossElasticity = [r'\underline{Assumed Elasticities:} \\', ' \n ',
    '\ \ \small{ Common Parameters }', 
    '\n', elasticity_results_string[0], ' \n',
    '\ \ \small{ Low Elasticity (0.15) }', 
    '\n', elasticity_results_string[1], ' \n',
    '\ \ \small{ Medium Elasticity (0.30) }', 
    '\n', elasticity_results_string[2], ' \n',
    '\ \ \small{ High Elasticity (0.45) }',
    '\n', elasticity_results_string[3], ' \n',
    '\\\\', ' \n'] 

acrossRho = [r'\underline{Substitutability ($\rho$)} \\', ' \n ',
    '\ \ \small{ Perfect Substitutes }', 
    ' \n', rho_results_string[0], ' \n',
    '\ \ \small{ Gross Substitutes }', 
    '\n', rho_results_string[1], ' \n',
    '\ \ \small{ Cobb-Douglas }', 
    ' \n', rho_results_string[2], ' \n',
    '\\\\', ' \n'] 

acrossCollegeDef = [r'\underline{College Definitions:} \\', ' \n ',
    '\ \ \small{ Bachelor\'s or More  }', 
    '\n', collegeDef_results_string[0], ' \n',
    '\ \ \small{  Associate\'s or More  }', 
    '\n', collegeDef_results_string[1], ' \n',
    '\ \ \small{ Some College or More  }',
    '\n', collegeDef_results_string[2], ' \n',
    '\\\\', ' \n'] 

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("ResultsSummary.tex","w")
file.writelines(header) 
file.writelines(baseline)  
file.writelines(acrossTau)  
file.writelines(acrossElasticity)  
file.writelines(acrossRho)  
file.writelines(acrossCollegeDef)   
file.writelines(closer)   
file.close()