#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 12:09:03 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder = main_folder +"/output/Graphs/Time Varying Tau"
os.chdir(code_folder)

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model 

# Import plotting packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False


#%%  Import Data and Compile Dataframe #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('CPS_ASEC_clean.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard/Emily:
os.chdir(data_folder + "/Time Series from Emily")
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)


# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'epop_ratio': OECD_data['Employment Rate (25-64)']/100,
                'pop_count': OECD_data['Population (25-64)'],
                'share_pop_c': ASEC_data['share_pop_c (weighted)'],
                'share_workers1_c': ASEC_data['share_workers1_c (weighted)'],
                'wage1_c': ASEC_data['wage1_c (weighted)'],
                'wage1_n': ASEC_data['wage1_n (weighted)'],
                'P1_c': ASEC_data['P1_c (weighted)'],
                'P1_n': ASEC_data['P1_n (weighted)'],
                'tau_high': premium_data['Avg Enr Cost'],
                'tau_baseline': premium_data['Avg Enr Cost']*ASEC_data.loc[2019,'Share ESHI policyholders (weighted)'],
                'tau_dynamic':premium_data['Avg Enr Cost']*ASEC_data['Share ESHI policyholders (weighted)'].backfill(), #Added for this Appendix
                'tau_low': premium_data['Avg Emp Cost']**ASEC_data['Share ESHI policyholders (weighted)'].backfill(),
                'Share ESHI policyholders':ASEC_data['Share ESHI policyholders (weighted)'],
                'Share ESHI policyholders, College':ASEC_data['Share ESHI policyholders, College (weighted)'],
                'Share ESHI policyholders, Non-college':ASEC_data['Share ESHI policyholders, Non-college (weighted)']
            })


#%%  Analysis for Graphs  #%%  

### Set up
versions = ['Baseline', 'Dynamic']

years = [1977,1987] + list(range(1996, 2020))

versions2tau_Dict = {'Baseline':'tau_baseline', 
                      'Dynamic':'tau_dynamic'}

outcome_variables = ['Cost of ESHI',
                     'Payroll Tax Rate',
                     'Percentage Change in College Wage Premium',
                     'Change in Wages, College',
                     'Change in Wages, Non-college',
                     'Change in Employment Rate, College',
                     'Change in Employment Rate, Non-college',
                     'Change in Total Employment',
                     'Change in Employment, College',
                     'Change in Employment, Non-college',   
                     'Change in College Share of the Wage Bill']

### Parameters for Model Calibration
# Parameter assumptions:
alpha_c=1
alpha_n=1

# Baseline Parameters:
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


### Loop through and calculate
output = pd.DataFrame()
for version in versions:
    tau_param = versions2tau_Dict[version]
    
    for year in years:
        
        ### Calibrate model
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
    
    
        ### Make Calculations
        tau = model.tau
        payroll_tax = 100*model.t
        chg_w_C = model.w2_c - model.w1_c
        chg_w_N = model.w2_n - model.w1_n
        pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
        pp_chg_P_C = 100*(model.P2_c - model.P1_c)
        pp_chg_P_N = 100*(model.P2_n - model.P1_n)
        chg_employment = model.employment2 - model.employment1
        chg_employment_C = model.employment2_c - model.employment1_c
        chg_employment_N = model.employment2_n - model.employment1_n
        chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-\
                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
        
        ### Store results in output df
        output.loc[year, f'Cost of ESHI ({version})'] = tau
        output.loc[year, f'Payroll Tax Rate ({version})'] = payroll_tax
        output.loc[year, f'Percentage Change in College Wage Premium ({version})'] = pct_chg_cwp
        output.loc[year, f'Change in Wages, College ({version})'] = chg_w_C
        output.loc[year, f'Change in Wages, Non-college ({version})'] = chg_w_N
        output.loc[year, f'Change in Employment Rate, College ({version})'] = pp_chg_P_C
        output.loc[year, f'Change in Employment Rate, Non-college ({version})'] = pp_chg_P_N
        output.loc[year, f'Change in Total Employment ({version})'] = chg_employment
        output.loc[year, f'Change in Employment, College ({version})'] = chg_employment_C
        output.loc[year, f'Change in Employment, Non-college ({version})'] = chg_employment_N
        output.loc[year, f'Change in College Share of the Wage Bill ({version})'] = chg_cwb

#%%  Data Export #%%
'''
## Select relevant variables
data_export = output

## Export data
os.chdir(data_folder)
data_export.to_csv('output_time_varying_tau.csv')
'''
                     
#%%  Graphs  #%%
os.chdir(output_folder)
  
# Plot Share ESHI Policyholders
plt.plot(ASEC_data['Share ESHI policyholders (weighted)'], color='black')
plt.title('Share ESHI Policyholders', fontsize=14)
plt.ylim([0.5,1])
plt.savefig('Share ESHI Policyholders.png', dpi=500)
plt.clf() 


# Plot Outcome variables
versions2color_Dict = {'Baseline': 'navy', 
                      'Dynamic': 'maroon'}

for var in outcome_variables:
    for version in versions:
        plt.plot(output[var+f' ({version})'], label=version, \
                 color=versions2color_Dict[version])
    plt.title(var, fontsize=14)
    plt.legend()
    plt.savefig(f'{var}.png', dpi=500)
    plt.clf() 
        