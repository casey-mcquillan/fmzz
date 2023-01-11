#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 19:53:26 2022
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
from main import main_folder
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder = main_folder+"/output/Tables/"

### Import calibration class
os.chdir(code_folder)

#from fzz_calibration import calibration_model
from fzz_calibration import calibration_model

#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year1 = 1977
year2 = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Baseline Estimate      %%#
#Results for Overview Table
baseline_results_string_H = []
baseline_results_string_P = []
baseline_results_string_CG = []

#Define Models
model_year1 = calibration_model(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year1, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c=df_observed.loc[year1, 'wage1_c'], 
                    w1_n=df_observed.loc[year1, 'wage1_n'],
                    P1_c=df_observed.loc[year1, 'P1_c'], 
                    P1_n=df_observed.loc[year1, 'P1_n'],
                    share_workers1_c=df_observed.loc[year1, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year1, 'share_pop_c'],
                    pop_count=df_observed.loc[year1, 'pop_count'])


model_year2 = calibration_model(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year2, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c=df_observed.loc[year2, 'wage1_c'], 
                    w1_n=df_observed.loc[year2, 'wage1_n'],
                    P1_c=df_observed.loc[year2, 'P1_c'], 
                    P1_n=df_observed.loc[year2, 'P1_n'],
                    share_workers1_c=df_observed.loc[year2, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year2, 'share_pop_c'],
                    pop_count=df_observed.loc[year2, 'pop_count'])


## Make sure there are no NANs in model before calibration
# Remove elasticities if specified to be common
for model_num in [1, 2]:
    exec(f'model = model_year{model_num}')
    exec(f'year = year{model_num}')
    if model.elasticity_c == model.elasticity_n == 'common': 
        check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
    else: check = vars(model).keys()
    #And now check
    if any(np.isnan([vars(model)[x] for x in check])):
        print("NAN value entered into calibration model for:")
        for var in check:
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))

## Calibrate Models
model_year1.calibrate()
model_year2.calibrate()

## Save Results for Overview
#College Wage Premium
cwp_H_1 = (model_year1.w1_c/model_year1.w1_n)-1
cwp_H_2 = (model_year2.w1_c/model_year2.w1_n)-1

cwp_P_1 = (model_year1.w2_c/model_year1.w2_n)-1
cwp_P_2 = (model_year2.w2_c/model_year2.w2_n)-1

chg_cwp_H = 100*(cwp_H_2 - cwp_H_1)
chg_cwp_P = 100*(cwp_P_2 - cwp_P_1)
diff_chg_cwp = (chg_cwp_P-chg_cwp_H)

#Non-College wages
chg_w_N_H = model_year2.w1_n - model_year1.w1_n
chg_w_N_P = model_year2.w2_n - model_year1.w2_n

#College Employment Rate
chg_cer_H = 100*(model_year2.P1_c - model_year1.P1_c)
chg_cer_P = 100*(model_year2.P2_c - model_year1.P2_c)
diff_chg_cer = (chg_cer_P-chg_cer_H)

#Non-College Employment Rate
chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
diff_chg_ncer = (chg_ncer_P-chg_ncer_H)

#Non-College Employment
chg_nce_H = (model_year2.employment1_n - model_year1.employment1_n)/1000
chg_nce_P = (model_year2.employment2_n - model_year1.employment2_n)/1000
diff_chg_nce = (chg_nce_P-chg_nce_H)

#Payroll Tax Rate    
ptr_P_1 = 100*model_year1.t
ptr_P_2 = 100*model_year2.t
chg_ptr_P = (ptr_P_2 - ptr_P_1)
   
#Store Results
baseline_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & \\${chg_w_N_H:,.0f} & {chg_cer_H:,.2f} pp & {chg_ncer_H:,.2f} pp & - \\\\ ')
baseline_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & \\${chg_w_N_P:,.0f} & {chg_cer_P:,.2f} pp & {chg_ncer_P:,.2f} pp & {chg_ptr_P:,.2f} pp \\\\ ')
baseline_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cer:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')

    
#%%      Vary Elasticties:      %%#
#Results for Overview Table
elasticity_results_string_H = []
elasticity_results_string_P = []
elasticity_results_string_CG = []

# Parameter to be varied:
elasticity_values = [['common','common'], [0.15,0.15],[0.3,0.3],[0.45,0.45]]
elasticity2specification_Dict ={str(['common','common']):'Common $\kappa$',
                         str([0.15,0.15]): 'Low (0.15)',
                         str([0.3,0.3]): 'Medium (0.30)',
                         str([0.45,0.45]): 'High (0.45)'}

# Loop through elasticity pairs in calibration process
i = 0
for elasticity_value in elasticity_values:
    i = i+1
    e_c, e_n, = elasticity_value[0], elasticity_value[1]
    label = elasticity2specification_Dict[str(elasticity_value)]
    
    #Define and calibrate model
    model_year1 = calibration_model(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year1, tau_baseline],
                elasticity_c=e_c, elasticity_n=e_n,
                w1_c=df_observed.loc[year1, 'wage1_c'], 
                w1_n=df_observed.loc[year1, 'wage1_n'],
                P1_c=df_observed.loc[year1, 'P1_c'], 
                P1_n=df_observed.loc[year1, 'P1_n'],
                share_workers1_c=df_observed.loc[year1, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year1, 'share_pop_c'],
                pop_count=df_observed.loc[year1, 'pop_count'])
    
    model_year2 = calibration_model(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year2, tau_baseline],
                elasticity_c=e_c, elasticity_n=e_n,
                w1_c=df_observed.loc[year2, 'wage1_c'], 
                w1_n=df_observed.loc[year2, 'wage1_n'],
                P1_c=df_observed.loc[year2, 'P1_c'], 
                P1_n=df_observed.loc[year2, 'P1_n'],
                share_workers1_c=df_observed.loc[year2, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year2, 'share_pop_c'],
                pop_count=df_observed.loc[year2, 'pop_count'])
    
    ## Make sure there are no NANs in model before calibration
    # Remove elasticities if specified to be common
    for model_num in [1, 2]:
        exec(f'model = model_year{model_num}')
        exec(f'year = year{model_num}')
        if model.elasticity_c == model.elasticity_n == 'common': 
            check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
        else: check = vars(model).keys()
        #And now check
        if any(np.isnan([vars(model)[x] for x in check])):
            print("NAN value entered into calibration model for:")
            for var in check:
                if np.isnan(vars(model)[var])==True: print("    "+var)
            print("for year: " + str(year))
            continue
        
    ## Calibrate Models
    model_year1.calibrate()
    model_year2.calibrate()
    
    ## Save Results for Overview
    #College Wage Premium
    cwp_H_1 = (model_year1.w1_c/model_year1.w1_n)-1
    cwp_H_2 = (model_year2.w1_c/model_year2.w1_n)-1
    
    cwp_P_1 = (model_year1.w2_c/model_year1.w2_n)-1
    cwp_P_2 = (model_year2.w2_c/model_year2.w2_n)-1
    
    chg_cwp_H = 100*(cwp_H_2 - cwp_H_1)
    chg_cwp_P = 100*(cwp_P_2 - cwp_P_1)
    diff_chg_cwp = (chg_cwp_P-chg_cwp_H)
    
    #Non-College wages
    chg_w_N_H = model_year2.w1_n - model_year1.w1_n
    chg_w_N_P = model_year2.w2_n - model_year1.w2_n
    
    #College Employment Rate
    chg_cer_H = 100*(model_year2.P1_c - model_year1.P1_c)
    chg_cer_P = 100*(model_year2.P2_c - model_year1.P2_c)
    diff_chg_cer = (chg_cer_P-chg_cer_H)
    
    #Non-College Employment Rate
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    #Non-College Employment
    chg_nce_H = (model_year2.employment1_n - model_year1.employment1_n)/1000
    chg_nce_P = (model_year2.employment2_n - model_year1.employment2_n)/1000
    diff_chg_nce = (chg_nce_P-chg_nce_H)
    
    #Payroll Tax Rate    
    ptr_P_1 = 100*model_year1.t
    ptr_P_2 = 100*model_year2.t
    chg_ptr_P = (ptr_P_2 - ptr_P_1)
    
    #Store Results
    elasticity_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & \\${chg_w_N_H:,.0f} & {chg_cer_H:,.2f} pp & {chg_ncer_H:,.2f} pp & - \\\\ ')
    elasticity_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & \\${chg_w_N_P:,.0f} & {chg_cer_P:,.2f} pp & {chg_ncer_P:,.2f} pp & {chg_ptr_P:,.2f} pp \\\\ ')
    elasticity_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cer:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')

#%%      Vary Substitutabilitity:      %%#
#Results for Overview Table
rho_results_string_H = []
rho_results_string_P = []
rho_results_string_CG = []

# Parameter to be varied:
rho_values = [1, 0.3827, 0.01]
rho2specification_Dict ={str(1):'Perfect Substitutes',
                         str(0.3827): 'Gross Substitutes',
                         str(0.01): 'Cobb-Douglas'}

# Loop through rho values in calibration process
i = 0
for rho_value in rho_values:
    i = i+1
    label = rho2specification_Dict[str(rho_value)]
    
    #Define and calibrate model    
    model_year1 = calibration_model(alpha_c, alpha_n,
                rho=rho_value,
                tau=df_observed.loc[year1, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                w1_c=df_observed.loc[year1, 'wage1_c'], 
                w1_n=df_observed.loc[year1, 'wage1_n'],
                P1_c=df_observed.loc[year1, 'P1_c'], 
                P1_n=df_observed.loc[year1, 'P1_n'],
                share_workers1_c=df_observed.loc[year1, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year1, 'share_pop_c'],
                pop_count=df_observed.loc[year1, 'pop_count'])

    model_year2 = calibration_model(alpha_c, alpha_n,
                rho=rho_value,
                tau=df_observed.loc[year2, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                w1_c=df_observed.loc[year2, 'wage1_c'], 
                w1_n=df_observed.loc[year2, 'wage1_n'],
                P1_c=df_observed.loc[year2, 'P1_c'], 
                P1_n=df_observed.loc[year2, 'P1_n'],
                share_workers1_c=df_observed.loc[year2, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year2, 'share_pop_c'],
                pop_count=df_observed.loc[year2, 'pop_count'])

    ## Make sure there are no NANs in model before calibration
    # Remove elasticities if specified to be common
    for model_num in [1, 2]:
        exec(f'model = model_year{model_num}')
        exec(f'year = year{model_num}')
        if model.elasticity_c == model.elasticity_n == 'common': 
            check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
        else: check = vars(model).keys()
        #And now check
        if any(np.isnan([vars(model)[x] for x in check])):
            print("NAN value entered into calibration model for:")
            for var in check:
                if np.isnan(vars(model)[var])==True: print("    "+var)
            print("for year: " + str(year))
            continue
        
    ## Calibrate Models
    model_year1.calibrate()
    model_year2.calibrate()
    
    ## Save Results for Overview
    #College Wage Premium
    cwp_H_1 = (model_year1.w1_c/model_year1.w1_n)-1
    cwp_H_2 = (model_year2.w1_c/model_year2.w1_n)-1
    
    cwp_P_1 = (model_year1.w2_c/model_year1.w2_n)-1
    cwp_P_2 = (model_year2.w2_c/model_year2.w2_n)-1
    
    chg_cwp_H = 100*(cwp_H_2 - cwp_H_1)
    chg_cwp_P = 100*(cwp_P_2 - cwp_P_1)
    diff_chg_cwp = (chg_cwp_P-chg_cwp_H)
    
    #Non-College wages
    chg_w_N_H = model_year2.w1_n - model_year1.w1_n
    chg_w_N_P = model_year2.w2_n - model_year1.w2_n

    #College Employment Rate
    chg_cer_H = 100*(model_year2.P1_c - model_year1.P1_c)
    chg_cer_P = 100*(model_year2.P2_c - model_year1.P2_c)
    diff_chg_cer = (chg_cer_P-chg_cer_H)
    
    #Non-College Employment Rate
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    #Non-College Employment
    chg_nce_H = (model_year2.employment1_n - model_year1.employment1_n)/1000
    chg_nce_P = (model_year2.employment2_n - model_year1.employment2_n)/1000
    diff_chg_nce = (chg_nce_P-chg_nce_H)
    
    #Payroll Tax Rate    
    ptr_P_1 = 100*model_year1.t
    ptr_P_2 = 100*model_year2.t
    chg_ptr_P = (ptr_P_2 - ptr_P_1)
    
    #Store Results
    rho_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & \\${chg_w_N_H:,.0f} & {chg_cer_H:,.2f} pp & {chg_ncer_H:,.2f} pp & - \\\\ ')
    rho_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & \\${chg_w_N_P:,.0f} & {chg_cer_P:,.2f} pp & {chg_ncer_P:,.2f} pp & {chg_ptr_P:,.2f} pp \\\\ ')
    rho_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cer:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')   


#%%      Compile and Export LaTeX file:      %%#        
## LaTeX code for header
header = ['\\begin{tabular}{lccccc}', '\n',
          '\\FL', '\n',
            '\t &    \multicolumn{1}{p{2.7cm}}{\\footnotesize \centering Change in College \\\\ Wage Premium $(w_C/w_N - 1)_{2019} - (w_C/w_N - 1)_{1977}$}', ' \n',
            '\t &	 \multicolumn{1}{p{2.6cm}}{\\footnotesize \centering Change in Non-College \\\\ Wages $w_{N,2019}-w_{N,1977}$}', ' \n',
            '\t &	 \multicolumn{1}{p{2.6cm}}{\\footnotesize \centering Change in College \\\\ Employment Rate $P_{C,2019}-P_{C,1977}$}', ' \n',
            '\t &	 \multicolumn{1}{p{2.6cm}}{\\footnotesize \centering Change in Non-College \\\\ Employment Rate $P_{N,2019}-P_{N,1977}$}', ' \n',
            '\t &	 \multicolumn{1}{p{2.6cm}}{\\footnotesize \centering Change in Payroll \\\\ Tax Rate \\\\ $t_{2019}-t_{1977}$}','\\\\', '\n',
            '\cmidrule{1-6}', '\n']  

## LaTeX code for table results
headTax = ['\\\\', ' \n',
           r'\textbf{Head Tax Equilibrium}',
           '\n', baseline_results_string_H[0], ' \n',
           '\\\\', ' \n'] 

payrollTax = ['\cmidrule{1-6}', ' \n ',
              r'\textbf{Payroll Tax Equilibrium} \\ ', ' \n ',
              '\\\\', ' \n ']

baseline_P = [r'\ \ \underline{Baseline:}', ' \n', 
          baseline_results_string_P[0], ' \n',
          '\\\\', ' \n'] 

acrossElasticity = [r'\underline{Labor Supply Elasticities:} \\', ' \n',
    '\ \small{Derived Group-Specific Elasticities:} \\\\', ' \n ',
    '\ \ \ \ \small{$\epsilon_C=0.42$ and $\epsilon_N=0.28$ (Baseline)}', 
    '\n', elasticity_results_string_P[0], ' \n',
    '\ \small{Assumed Common Elasticities:} \\\\', ' \n',
    '\ \ \ \ \small{$\epsilon_C=\epsilon_N=0.15$}', 
    '\n', elasticity_results_string_P[1], ' \n',
    '\ \ \ \ \small{$\epsilon_C=\epsilon_N=0.30$}', 
    '\n', elasticity_results_string_P[2], ' \n',
    '\ \ \ \ \small{$\epsilon_C=\epsilon_N=0.45$}',
    '\n', elasticity_results_string_P[3], ' \n',
    '\\\\', ' \n'] 

acrossRho = [r'\underline{Substitutability ($\rho$)} \\', ' \n',
    '\ \ \ \ \small{Perfect Substitutes ($\\rho=1$)}', 
    ' \n', rho_results_string_P[0], ' \n',
    '\ \ \ \ \small{Gross Substitutes ($\\rho=0.38$, Baseline)}', 
    '\n', rho_results_string_P[1], ' \n',
    '\ \ \ \ \small{Cobb-Douglas ($\\rho=0$)}', 
    ' \n', rho_results_string_P[2], ' \n',
    '\\\\', ' \n'] 
# Concatenate table values
table_values = headTax + payrollTax + acrossRho + acrossElasticity 

## LaTeX code for closer
closer = ['\\bottomrule','\n', '\end{tabular}']

## Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

## Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"CounterfactualGrowth_Robustness.tex","w")
file.writelines(header) 
file.writelines(table_values)
file.writelines(closer)   
file.close()