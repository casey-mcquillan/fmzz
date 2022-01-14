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
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/ZidarOverview_CG'

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
year1 = 1987
year2 = 2019

#Baseline Parameters
tau_baseline = 'tau_high'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Baseline Estimate      %%#
#Results for Overview Table
baseline_results_string_H = []
baseline_results_string_P = []
baseline_results_string_CG = []

#Define Models
model_year1 = calibration_model_RC4(alpha_c, alpha_n,
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


model_year2 = calibration_model_RC4(alpha_c, alpha_n,
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

#College Wage Bill
cwb_H_1 = (model_year1.w1_c*model_year1.L1_c)/\
    (model_year1.w1_c*model_year1.L1_c + model_year1.w1_n*model_year1.L1_n)
cwb_H_2 = (model_year2.w1_c*model_year2.L1_c)/\
    (model_year2.w1_c*model_year2.L1_c + model_year2.w1_n*model_year2.L1_n)

cwb_P_1 = (model_year1.w2_c*model_year1.L2_c)/\
    (model_year1.w2_c*model_year1.L2_c + model_year1.w2_n*model_year1.L2_n)
cwb_P_2 = (model_year2.w2_c*model_year2.L2_c)/\
    (model_year2.w2_c*model_year2.L2_c + model_year2.w2_n*model_year2.L2_n)

chg_cwb_H = 100*(cwb_H_2 - cwb_H_1)
chg_cwb_P = 100*(cwb_P_2 - cwb_P_1)
diff_chg_cwb = (chg_cwb_P-chg_cwb_H)

#Non-College Employment Rate
ncer_H_1 = model_year1.P1_n
ncer_H_2 = model_year2.P1_n

ncer_H_1 = model_year1.P2_n
ncer_H_2 = model_year2.P2_n

chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
diff_chg_ncer = (chg_ncer_P-chg_ncer_H)

baseline_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & {chg_cwb_H:,.2f} pp & {chg_ncer_H:,.2f} pp \\\\ ')
baseline_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & {chg_cwb_P:,.2f} pp & {chg_ncer_P:,.2f} pp \\\\ ')
baseline_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cwb:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')

#%%      Vary Tau:      %%#
#Results for Overview Table
tau_results_string_H = []
tau_results_string_P = []
tau_results_string_CG = []

#Parameters to be varied:
tau_params = ['tau_high', 'tau_med']
tau2specification_Dict ={'tau_high':'Total Cost with Complete Take-up',
                         'tau_med':'Cost to Employer with Complete Take-up',
                         'tau_low':'Cost to Employer with Incomplete Take-up'}

#Loop through
i = 0
for tau_param in tau_params:
    i = i+1
    label = tau2specification_Dict[tau_param]
    
    #Define Model
    model_year1 = calibration_model_RC4(alpha_c, alpha_n,
                        rho=rho_baseline,
                        tau=df_observed.loc[year1, tau_param],
                        elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                        w1_c=df_observed.loc[year1, 'wage1_c'], 
                        w1_n=df_observed.loc[year1, 'wage1_n'],
                        P1_c=df_observed.loc[year1, 'P1_c'], 
                        P1_n=df_observed.loc[year1, 'P1_n'],
                        share_workers1_c=df_observed.loc[year1, 'share_workers1_c'],
                        share_pop_c=df_observed.loc[year1, 'share_pop_c'],
                        pop_count=df_observed.loc[year1, 'pop_count'])
    
    model_year2 = calibration_model_RC4(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year2, tau_param],
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
    
    #College Wage Bill
    cwb_H_1 = (model_year1.w1_c*model_year1.L1_c)/\
        (model_year1.w1_c*model_year1.L1_c + model_year1.w1_n*model_year1.L1_n)
    cwb_H_2 = (model_year2.w1_c*model_year2.L1_c)/\
        (model_year2.w1_c*model_year2.L1_c + model_year2.w1_n*model_year2.L1_n)
    
    cwb_P_1 = (model_year1.w2_c*model_year1.L2_c)/\
        (model_year1.w2_c*model_year1.L2_c + model_year1.w2_n*model_year1.L2_n)
    cwb_P_2 = (model_year2.w2_c*model_year2.L2_c)/\
        (model_year2.w2_c*model_year2.L2_c + model_year2.w2_n*model_year2.L2_n)
    
    chg_cwb_H = 100*(cwb_H_2 - cwb_H_1)
    chg_cwb_P = 100*(cwb_P_2 - cwb_P_1)
    diff_chg_cwb = (chg_cwb_P-chg_cwb_H)
    
    #Non-College Employment Rate
    ncer_H_1 = model_year1.P1_n
    ncer_H_2 = model_year2.P1_n
    
    ncer_H_1 = model_year1.P2_n
    ncer_H_2 = model_year2.P2_n
    
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    tau_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & {chg_cwb_H:,.2f} pp & {chg_ncer_H:,.2f} pp \\\\ ')
    tau_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & {chg_cwb_P:,.2f} pp & {chg_ncer_P:,.2f} pp \\\\ ')
    tau_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cwb:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')

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
    model_year1 = calibration_model_RC4(alpha_c, alpha_n,
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
    
    model_year2 = calibration_model_RC4(alpha_c, alpha_n,
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
    
    #College Wage Bill
    cwb_H_1 = (model_year1.w1_c*model_year1.L1_c)/\
        (model_year1.w1_c*model_year1.L1_c + model_year1.w1_n*model_year1.L1_n)
    cwb_H_2 = (model_year2.w1_c*model_year2.L1_c)/\
        (model_year2.w1_c*model_year2.L1_c + model_year2.w1_n*model_year2.L1_n)
    
    cwb_P_1 = (model_year1.w2_c*model_year1.L2_c)/\
        (model_year1.w2_c*model_year1.L2_c + model_year1.w2_n*model_year1.L2_n)
    cwb_P_2 = (model_year2.w2_c*model_year2.L2_c)/\
        (model_year2.w2_c*model_year2.L2_c + model_year2.w2_n*model_year2.L2_n)
    
    chg_cwb_H = 100*(cwb_H_2 - cwb_H_1)
    chg_cwb_P = 100*(cwb_P_2 - cwb_P_1)
    diff_chg_cwb = (chg_cwb_P-chg_cwb_H)
    
    #Non-College Employment Rate
    ncer_H_1 = model_year1.P1_n
    ncer_H_2 = model_year2.P1_n
    
    ncer_H_1 = model_year1.P2_n
    ncer_H_2 = model_year2.P2_n
    
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    elasticity_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & {chg_cwb_H:,.2f} pp & {chg_ncer_H:,.2f} pp \\\\ ')
    elasticity_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & {chg_cwb_P:,.2f} pp & {chg_ncer_P:,.2f} pp \\\\ ')
    elasticity_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cwb:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')

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
    model_year1 = calibration_model_RC4(alpha_c, alpha_n,
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

    model_year2 = calibration_model_RC4(alpha_c, alpha_n,
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
    
    #College Wage Bill
    cwb_H_1 = (model_year1.w1_c*model_year1.L1_c)/\
        (model_year1.w1_c*model_year1.L1_c + model_year1.w1_n*model_year1.L1_n)
    cwb_H_2 = (model_year2.w1_c*model_year2.L1_c)/\
        (model_year2.w1_c*model_year2.L1_c + model_year2.w1_n*model_year2.L1_n)
    
    cwb_P_1 = (model_year1.w2_c*model_year1.L2_c)/\
        (model_year1.w2_c*model_year1.L2_c + model_year1.w2_n*model_year1.L2_n)
    cwb_P_2 = (model_year2.w2_c*model_year2.L2_c)/\
        (model_year2.w2_c*model_year2.L2_c + model_year2.w2_n*model_year2.L2_n)
    
    chg_cwb_H = 100*(cwb_H_2 - cwb_H_1)
    chg_cwb_P = 100*(cwb_P_2 - cwb_P_1)
    diff_chg_cwb = (chg_cwb_P-chg_cwb_H)
    
    #Non-College Employment Rate
    ncer_H_1 = model_year1.P1_n
    ncer_H_2 = model_year2.P1_n
    
    ncer_H_1 = model_year1.P2_n
    ncer_H_2 = model_year2.P2_n
    
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    rho_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & {chg_cwb_H:,.2f} pp & {chg_ncer_H:,.2f} pp \\\\ ')
    rho_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & {chg_cwb_P:,.2f} pp & {chg_ncer_P:,.2f} pp \\\\ ')
    rho_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cwb:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')   

#%%      Vary College Definition:      %%#
#Results for Overview Table
collegeDef_results_string_H = []
collegeDef_results_string_P = []
collegeDef_results_string_CG = []

#Parameter to be varies
college_defs = [1, 2, 3]
college_defs2specification_Dict ={1:'Bachelor\s Degree or Higher',
                         2:'Associate\'s Degree or Higher',
                         3:'Some College or More'}

#Loop through vcollege definitions
i = 0
for def_num in [1,2,3]:  
    i = i+1 
    label = college_defs2specification_Dict[def_num]
    
    #Define and calibrate model
    model_year1 = calibration_model_RC4(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year1, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_c_baseline,
                w1_c=df_observed_RC1.loc[year1, f'wage1_c [college definition {def_num}]'], 
                w1_n=df_observed_RC1.loc[year1, f'wage1_n [college definition {def_num}]'],
                P1_c=df_observed_RC1.loc[year1, f'P1_c [college definition {def_num}]'], 
                P1_n=df_observed_RC1.loc[year1, f'P1_n [college definition {def_num}]'],
                share_workers1_c=df_observed_RC1.loc[year1, f'share_workers1_c [college definition {def_num}]'],
                share_pop_c=df_observed_RC1.loc[year1, f'share_pop_c [college definition {def_num}]'],
                pop_count=df_observed_RC1.loc[year1, 'pop_count'])
    
    model_year2 = calibration_model_RC4(alpha_c, alpha_n,
            rho=rho_baseline,
            tau=df_observed.loc[year2, tau_baseline],
            elasticity_c=e_c_baseline, elasticity_n=e_c_baseline,
            w1_c=df_observed_RC1.loc[year2, f'wage1_c [college definition {def_num}]'], 
            w1_n=df_observed_RC1.loc[year2, f'wage1_n [college definition {def_num}]'],
            P1_c=df_observed_RC1.loc[year2, f'P1_c [college definition {def_num}]'], 
            P1_n=df_observed_RC1.loc[year2, f'P1_n [college definition {def_num}]'],
            share_workers1_c=df_observed_RC1.loc[year2, f'share_workers1_c [college definition {def_num}]'],
            share_pop_c=df_observed_RC1.loc[year2, f'share_pop_c [college definition {def_num}]'],
            pop_count=df_observed_RC1.loc[year2, 'pop_count'])

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
    
    #College Wage Bill
    cwb_H_1 = (model_year1.w1_c*model_year1.L1_c)/\
        (model_year1.w1_c*model_year1.L1_c + model_year1.w1_n*model_year1.L1_n)
    cwb_H_2 = (model_year2.w1_c*model_year2.L1_c)/\
        (model_year2.w1_c*model_year2.L1_c + model_year2.w1_n*model_year2.L1_n)
    
    cwb_P_1 = (model_year1.w2_c*model_year1.L2_c)/\
        (model_year1.w2_c*model_year1.L2_c + model_year1.w2_n*model_year1.L2_n)
    cwb_P_2 = (model_year2.w2_c*model_year2.L2_c)/\
        (model_year2.w2_c*model_year2.L2_c + model_year2.w2_n*model_year2.L2_n)
    
    chg_cwb_H = 100*(cwb_H_2 - cwb_H_1)
    chg_cwb_P = 100*(cwb_P_2 - cwb_P_1)
    diff_chg_cwb = (chg_cwb_P-chg_cwb_H)
    
    #Non-College Employment Rate
    ncer_H_1 = model_year1.P1_n
    ncer_H_2 = model_year2.P1_n
    
    ncer_H_1 = model_year1.P2_n
    ncer_H_2 = model_year2.P2_n
    
    chg_ncer_H = 100*(model_year2.P1_n - model_year1.P1_n)
    chg_ncer_P = 100*(model_year2.P2_n - model_year1.P2_n)
    diff_chg_ncer = (chg_ncer_P-chg_ncer_H)
    
    collegeDef_results_string_H.append(f' \t & {chg_cwp_H:,.2f} pp & {chg_cwb_H:,.2f} pp & {chg_ncer_H:,.2f} pp \\\\ ')
    collegeDef_results_string_P.append(f' \t & {chg_cwp_P:,.2f} pp & {chg_cwb_P:,.2f} pp & {chg_ncer_P:,.2f} pp \\\\ ')
    collegeDef_results_string_CG.append(f' \t & {diff_chg_cwp:,.2f} pp & {diff_chg_cwb:,.2f} pp & {diff_chg_ncer:,.2f} pp \\\\ ')  

#%%      Compile Overview Tables:      %%#

## Table 1: Results under different counterfactuals
header = ['\ctable[caption={', f'Change over Time under Different Counterfactuals ({year1}-{year2})', '},', ' \n',
            '    label={SummaryOverview}, pos=h!]', ' \n',
            '{lccc}{}{\\FL', '\n',
            '\t &    \small \multicolumn{1}{p{3cm}}{\centering Chg. College \\\\ Wage Premium}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3cm}}{\centering  Chg. College \\\\ Wage Bill}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3.5cm}}{\centering Chg. Non-College \\\\ Employment Rate}', '\\\\', '\n',
            '\cmidrule{1-4}', '\n']  

headTax = [r'\textbf{Head Tax Equilibrium} \\', ' \n', 
          '\\\\', ' \n'] 

baseline_H = [r'\ \ \underline{Baseline:}', ' \n', 
          baseline_results_string_H[0], ' \n',
          '\\\\', ' \n'] 

acrossCollegeDef_H = [r'\ \ \underline{College Definitions:} \\', ' \n ',
    '\ \ \small{ Bachelor\'s or More  }', 
    '\n', collegeDef_results_string_H[0], ' \n',
    '\ \ \small{  Associate\'s or More  }', 
    '\n', collegeDef_results_string_H[1], ' \n',
    '\ \ \small{ Some College or More  }',
    '\n', collegeDef_results_string_H[2], ' \n',
    '\\\\', ' \n'] 


payrollTax = ['\cmidrule{1-4}', ' \n ',
              r'\textbf{Payroll Tax Equilibrium} \\ ', ' \n ',
              '\\\\', ' \n ']

baseline_P = [r'\ \ \underline{Baseline:}', ' \n', 
          baseline_results_string_P[0], ' \n',
          '\\\\', ' \n'] 

acrossTau = [r'\ \ \underline{Cost of ESHI:} \\', ' \n ',
    '\ \ \ \ \small \shortstack[l]{Total Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string_P[0], ' \n',
    '\ \ \ \ \small \shortstack[l]{Employer Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string_P[1], ' \n',
    '\\\\', ' \n ',] 

acrossElasticity = [r'\ \ \underline{Assumed Elasticities:} \\', ' \n ',
    '\ \ \ \ \small{ Common Parameters }', 
    '\n', elasticity_results_string_P[0], ' \n',
    '\ \ \ \ \small{ Low Elasticity (0.15) }', 
    '\n', elasticity_results_string_P[1], ' \n',
    '\ \ \ \ \small{ Medium Elasticity (0.30) }', 
    '\n', elasticity_results_string_P[2], ' \n',
    '\ \ \ \ \small{ High Elasticity (0.45) }',
    '\n', elasticity_results_string_P[3], ' \n',
    '\\\\', ' \n'] 

acrossRho = [r'\ \ \underline{Substitutability ($\rho$)} \\', ' \n ',
    '\ \ \ \ \small{ Perfect Substitutes }', 
    ' \n', rho_results_string_P[0], ' \n',
    '\ \ \ \ \small{ Gross Substitutes }', 
    '\n', rho_results_string_P[1], ' \n',
    '\ \ \ \ \small{ Cobb-Douglas }', 
    ' \n', rho_results_string_P[2], ' \n',
    '\\\\', ' \n'] 

acrossCollegeDef_P = [r'\ \ \underline{College Definitions:} \\', ' \n ',
    '\ \ \small{ Bachelor\'s or More  }', 
    '\n', collegeDef_results_string_P[0], ' \n',
    '\ \ \small{  Associate\'s or More  }', 
    '\n', collegeDef_results_string_P[1], ' \n',
    '\ \ \small{ Some College or More  }',
    '\n', collegeDef_results_string_P[2], ' \n',
    '\\\\', ' \n'] 

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open(f"Results_OverTime{year2}_{year1}.tex","w")
file.writelines(header) 
file.writelines(headTax)
file.writelines(baseline_H) 
file.writelines(acrossCollegeDef_H)  
file.writelines(payrollTax)  
file.writelines(baseline_P)   
file.writelines(acrossTau)  
file.writelines(acrossElasticity)  
file.writelines(acrossRho)  
file.writelines(acrossCollegeDef_P)   
file.writelines(closer)   
file.close()
 
    

## Table 2: Difference in Counterfactuals
header = ['\ctable[caption={', f'Difference in Growth (Payroll Tax versus Head Tax, {year1}-{year2})', '},', ' \n',
            '    label={DifferenceOverview}, pos=h!]', ' \n',
            '{lccc}{}{\\FL', '\n',
            '\t &    \small \multicolumn{1}{p{3cm}}{\centering Chg. College \\\\ Wage Premium}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3cm}}{\centering  Chg. College \\\\ Wage Bill}', ' \n',
            '\t &	 \small \multicolumn{1}{p{3.5cm}}{\centering Chg. Non-College \\\\ Employment Rate}', '\\\\', '\n',
            '\cmidrule{1-4}', '\\\\', ' \n']  

baseline = [r'\ \ \underline{Baseline:}', ' \n', 
          baseline_results_string_CG[0], ' \n',
          '\\\\', ' \n'] 

acrossTau = [r'\ \ \underline{Cost of ESHI:} \\', ' \n ',
    '\ \ \ \ \small \shortstack[l]{Total Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string_CG[0], ' \n',
    '\ \ \ \ \small \shortstack[l]{Employer Cost with \\\\ \ \ Complete Take-up}', 
    ' \n', tau_results_string_CG[1], ' \n',
    '\\\\', ' \n ',] 

acrossElasticity = [r'\ \ \underline{Assumed Elasticities:} \\', ' \n ',
    '\ \ \ \ \small{ Common Parameters }', 
    '\n', elasticity_results_string_CG[0], ' \n',
    '\ \ \ \ \small{ Low Elasticity (0.15) }', 
    '\n', elasticity_results_string_CG[1], ' \n',
    '\ \ \ \ \small{ Medium Elasticity (0.30) }', 
    '\n', elasticity_results_string_CG[2], ' \n',
    '\ \ \ \ \small{ High Elasticity (0.45) }',
    '\n', elasticity_results_string_CG[3], ' \n',
    '\\\\', ' \n'] 

acrossRho = [r'\ \ \underline{Substitutability ($\rho$)} \\', ' \n ',
    '\ \ \ \ \small{ Perfect Substitutes }', 
    ' \n', rho_results_string_CG[0], ' \n',
    '\ \ \ \ \small{ Gross Substitutes }', 
    '\n', rho_results_string_CG[1], ' \n',
    '\ \ \ \ \small{ Cobb-Douglas }', 
    ' \n', rho_results_string_CG[2], ' \n',
    '\\\\', ' \n'] 

acrossCollegeDef = [r'\ \ \underline{College Definitions:} \\', ' \n ',
    '\ \ \small{ Bachelor\'s or More  }', 
    '\n', collegeDef_results_string_CG[0], ' \n',
    '\ \ \small{  Associate\'s or More  }', 
    '\n', collegeDef_results_string_CG[1], ' \n',
    '\ \ \small{ Some College or More  }',
    '\n', collegeDef_results_string_CG[2], ' \n',
    '\\\\', ' \n'] 

closer = ['\\bottomrule}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_path)
file = open(f"Difference_OverTime{year2}_{year1}.tex","w")
file.writelines(header)   
file.writelines(baseline)   
file.writelines(acrossTau)  
file.writelines(acrossElasticity)  
file.writelines(acrossRho)  
file.writelines(acrossCollegeDef)   
file.writelines(closer)   
file.close()