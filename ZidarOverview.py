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
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/Overview'

### Import calibration class
os.chdir(code_folder)

#from fzz_calibration import calibration_model 
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
tau_baseline = 'tau_baseline'
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
                     location=output_path, subtitle=f' with Baseline Parameters')

model.generate_table(file_name='EqComparison'+str(year)+"_baseline", year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"_baseline", 
                     location=output_path, subtitle=f' with Baseline Parameters')

#Save Results for Overview
pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
chg_w_C = (model.w2_c - model.w1_c)
pp_chg_P_C = 100*(model.P2_c - model.P1_c)
pp_chg_P_N = 100*(model.P2_n - model.P1_n)
chg_employment_N = model.employment2_n - model.employment1_n
baselines_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')

#%%      Vary Tau:      %%#
#Results for Overview Table
tau_results_string = []

#Parameters to be varied:
#tau_params = ['tau_high', 'tau_baseline', 'tau_low']
tau_params = ['tau_baseline', 'tau_high']
tau2specification_Dict ={'tau_high':'Total Cost with Complete Takeup',
                         'tau_baseline':'Total Cost with Incomplete Takeup',
                         'tau_low':'Cost to Employer with Incomplete Takeup'}

#Initialize strings for tables
tau_string = '\\underline{Fixed Per Worker Cost, $\\tau$:} \n \t'
payroll_tax_string = '\\underline{Payroll Tax Rate, $t$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ Pct. Change in College Wage Premium, $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
delta_employment_string = 'Change in Total Employment, $\Delta(L)$ \n \t'
delta_employment_C_string = '\\ \\ \\small Change in College Employment, $\Delta(L_C)$ \n \t'
delta_employment_N_string = '\\ \\ \\small Change in Non-college Employment, $\Delta(L_N)$ \n \t'
delta_cwb_string = 'Change in College Share of Wage Bill, $\Delta(\\frac{w_C L_C}{w_N L_N+w_C L_C})$: \n \t'


#Loop through
i = 0
for tau_param in tau_params:
    i = i+1
    label = tau2specification_Dict[tau_param]
    
    #Define Model
    model = calibration_model(alpha_c, alpha_n,
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
    '''
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    pp_chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))\
                       -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)    
    chg_employment_N = model.employment2_n - model.employment1_n
    tau_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')
    '''
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
    
    tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
    payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '
    delta_w_C_string = delta_w_C_string + ampersand + f' \${model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${model.w2_n-model.w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P2_n-model.P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P2_c-model.P1_c):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'
    
header = ['\\begin{tabular}{lcccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(1)} \\\\ Baseline}','\n', 
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(2)} \\\\ Full Coverage}','\\\\','\n', 
          '\cmidrule{1-4}', '\n']

table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                payroll_tax_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

#Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

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
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
delta_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
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
    model = calibration_model(alpha_c, alpha_n,
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
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    chg_employment_N = model.employment2_n - model.employment1_n
    elasticity_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')

    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P2_n-model.P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P2_c-model.P1_c):,.2f} pp '
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
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
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
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
delta_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
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
    model = calibration_model(alpha_c, alpha_n,
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
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    chg_employment_N = model.employment2_n - model.employment1_n
    rho_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P2_n-model.P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P2_c-model.P1_c):,.2f} pp '
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
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
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
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
delta_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'

#Loop through College Definitions
i = 0
for def_num in [1,2,3]:  
    i = i+1 
    label = college_defs2specification_Dict[def_num]
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_c_baseline,
                w1_c=df_observed_RC1.loc[year, f'wage1_c [College Definition {def_num}]'], 
                w1_n=df_observed_RC1.loc[year, f'wage1_n [College Definition {def_num}]'],
                P1_c=df_observed_RC1.loc[year, f'P1_c [College Definition {def_num}]'], 
                P1_n=df_observed_RC1.loc[year, f'P1_n [College Definition {def_num}]'],
                share_workers1_c=df_observed_RC1.loc[year, f'share_workers1_c [College Definition {def_num}]'],
                share_pop_c=df_observed_RC1.loc[year, f'share_pop_c [College Definition {def_num}]'],
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
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    chg_employment_N = model.employment2_n - model.employment1_n
    
    collegeDef_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')
    
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P2_n-model.P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P2_c-model.P1_c):,.2f} pp '
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
          '\t &	 \multicolumn{1}{p{3cm}}{\small \centering Bachelor\'s Degree \\\\ or Higher}','\n', 
          '\t &&	 \multicolumn{1}{p{3cm}}{\small \centering  Associate\'s Degree \\\\ or Higher}','\n', 
          '\t &&	 \multicolumn{1}{p{3cm}}{\small \centering Some College \\\\ or More}', '\\\\', '\n', 
          '\cmidrule{1-6}', '\n']

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
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
header = ['\\begin{tabular}{lcccccc}', ' \n',
            '\\FL', '\n',
            '\t &    \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering Percent Change \\\\ in College \\\\ Wage Premium}', ' \n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-college Wages \\\\ $\Delta(w_N)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ College Employment \\\\ Rate \\\\ $\Delta(P_C)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-College Employment \\\\ Rate \\\\ $\Delta(P_C)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-College \\\\ Employment (Thous.) \\\\ $\Delta(L_N)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Payroll \\\\ Tax Rate \\\\ $t$}', '\\\\', '\n',
            '\cmidrule{1-7}', '\n',
            '\\\\' '\n']  

baseline = [r'\underline{Baseline:}', ' \n', 
          baselines_results_string[0], ' \n',
          '\\\\', ' \n'] 

# acrossTau = [r'\underline{Cost of ESHI:} \\', ' \n',
#     '\ \ \small \shortstack[l]{Total Cost with \\\\ \ \ Complete Takeup}', 
#     ' \n', tau_results_string[0], ' \n',
#     '\ \ \small \shortstack[l]{Total Cost with \\\\ \ \ Incomplete Takeup} (Baseline)', 
#     ' \n', tau_results_string[1], ' \n',
#     '\ \ \small \shortstack[l]{Employer Cost with \\\\ \ \ Incomplete Takeup}',
#     ' \n', tau_results_string[2], ' \n',
#     '\\\\', ' \n '] 

acrossElasticity = [r'\underline{Labor Supply Elasticities:} \\', ' \n',
    '\ \small{Derived Group-Specific Elasticities:} \\\\', ' \n ',
    '\ \ \ \small{$\epsilon_C=0.42$ and $\epsilon_N=0.28$ (Baseline)}', 
    '\n', elasticity_results_string[0], ' \n',
    '\ \small{Assumed Common Elasticities:} \\\\', ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.15$}', 
    '\n', elasticity_results_string[1], ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.30$}', 
    '\n', elasticity_results_string[2], ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.45$}',
    '\n', elasticity_results_string[3], ' \n',
    '\\\\', ' \n'] 

acrossRho = [r'\underline{Substitutability ($\rho$)} \\', ' \n',
    '\ \ \small{Perfect Substitutes ($\\rho=1$)}', 
    ' \n', rho_results_string[0], ' \n',
    '\ \ \small{Gross Substitutes ($\\rho=0.38$, Baseline)}', 
    '\n', rho_results_string[1], ' \n',
    '\ \ \small{Cobb-Douglas ($\\rho=0$)}', 
    ' \n', rho_results_string[2], ' \n',
    '\\\\', ' \n'] 

# acrossCollegeDef = [r'\underline{College Definitions:} \\', ' \n',
#     '\ \ \small{Bachelor\'s or More (Baseline)}', 
#     '\n', collegeDef_results_string[0], ' \n',
#     '\ \ \small{Associate\'s or More  }', 
#     '\n', collegeDef_results_string[1], ' \n',
#     '\ \ \small{Some College or More  }',
#     '\n', collegeDef_results_string[2], ' \n',
#     '\\\\', ' \n'] 

# Concatenate table values
table_values = baseline + acrossRho + acrossElasticity 

closer = ['\\bottomrule','\n', '\end{tabular}']

#Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open("Overview_Robustness.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer) 
file.close()
