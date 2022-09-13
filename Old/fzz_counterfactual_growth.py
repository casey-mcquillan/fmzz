#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 15:46:18 2021

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
output_path = "/Users/caseymcquillan/Desktop/"
#output_path = "/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Counterfactual Growth"
os.chdir(code_folder)


### Import calibration class
from fzz_calibration import calibration_model 


#%%  Importing Data #%%  
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%  Calculate Results over Time and across Tau #%%
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

#interpolate value of tau for 2007:
df_observed.loc[2007, 'tau_low'] = np.mean([df_observed.loc[2006, 'tau_low'], \
                                           df_observed.loc[2008, 'tau_low']])

# Parameter assumptions:
alpha_c, alpha_n, = 1, 1

# Parameter to be varied:
years = [1977,1987] + list(range(1996, 2020))
tau_params = ['tau_high', 'tau_med', 'tau_low']
tau2specification_Dict ={'tau_high':'Total Cost and Complete Take-up',
                         'df_observed':'Cost to Employer and Complete Take-up',
                         'tau_low':'Cost to Employer and Incomplete Take-up'}

#Loop through values of tau and year
df_outcomes = pd.DataFrame(columns = ['year', 'Tau',
                    "College Wage Premium (Head Tax)",
                    "College Wage Premium (Payroll Tax)",
                    "College Share of the Wage Bill (Head Tax)",
                    "College Share of the Wage Bill (Payroll Tax)",
                    "College Employment Rate (Head Tax)", 
                    "College Employment Rate (Payroll Tax)",
                    "Non-college Employment Rate (Head Tax)", 
                    "Non-college Employment Rate (Payroll Tax)"])

for tau in tau_params:  
    for year in years:
        #Define and calibrate model
        model = calibration_model(alpha_c, alpha_n,
                    tau=df_observed.loc[year, tau], 
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
        
        #Calculate variables of interest
        cwpRatio_h = model.w1_c / model.w1_n
        cwpRatio_p = model.w2_c / model.w2_n  
        
        cswb_h = (model.w1_c*model.L1_c) / (model.w1_c*model.L1_c + model.w1_n*model.L1_n)
        cswb_p = (model.w2_c*model.L2_c) / (model.w2_c*model.L2_c + model.w2_n*model.L2_n)
            
        
        #Create rows for dataframe and append them
        new_row = {'year':year, 'Tau':tau, \
                    "College Wage Premium (Head Tax)": cwpRatio_h, \
                    "College Wage Premium (Payroll Tax)": cwpRatio_p, \
                    "College Share of the Wage Bill (Head Tax)": cswb_h, \
                    "College Share of the Wage Bill (Payroll Tax)": cswb_p, \
                    "College Employment Rate (Head Tax)": model.P1_c, \
                    "College Employment Rate (Payroll Tax)": model.P2_c}
                    "Non-college Employment Rate (Head Tax)": model.P1_n, \
                    "Non-college Employment Rate (Payroll Tax)": model.P2_n}
        df_outcomes = df_outcomes.append(\
                    [new_row], ignore_index=True)
#Set year as index
df_outcomes=df_outcomes.set_index('year')   

#Create subsets based on college definition
for tau in tau_params:
    exec(f'df_{tau} = df_outcomes[df_outcomes[\'Tau\']==\'{tau}\']') 


#%%  Print and Graph Results #%%
# Import necessary Packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False
matplotlib.rcParams['axes.spines.bottom'] = False


# Calculate counterfactuals and graph:
os.chdir(output_path)
ref_year = 2019
for tau in tau_params:
    print(f'Tau Definition: {tau2specification_Dict[tau]}:')
    for year in [1977,1987,1997,2007]:
        if tau == 'tau_low' and year<1996: continue
        else:
            exec(f'chg_cwpRatio_h = (df_{tau}.loc[ref_year,\'College Wage Premium (Head Tax)\'] -' +\
                        f'df_{tau}.loc[year,\'College Wage Premium (Head Tax)\'])')
            exec(f'chg_cwpRatio_p = (df_{tau}.loc[ref_year,\'College Wage Premium (Payroll Tax)\'] -' +\
                        f'df_{tau}.loc[year,\'College Wage Premium (Payroll Tax)\'])')
            pct_diff_cwpRatio = -100*((chg_cwpRatio_p - chg_cwpRatio_h) / chg_cwpRatio_h)
            
            exec(f'chg_cswb_h = (df_{tau}.loc[ref_year,\'College Share of the Wage Bill (Head Tax)\'] - ' +\
                        f'df_{tau}.loc[year,\'College Share of the Wage Bill (Head Tax)\'])')
            exec(f'chg_cswb_p = (df_{tau}.loc[ref_year,\'College Share of the Wage Bill (Payroll Tax)\'] - ' +\
                        f'df_{tau}.loc[year,\'College Share of the Wage Bill (Payroll Tax)\'])')
            pct_diff_cswb = -100*((chg_cswb_p - chg_cswb_h) / chg_cswb_h)
                
                
            exec(f'chg_empRate_h = (df_{tau}.loc[ref_year,\'Non-college Employment Rate (Head Tax)\'] - ' +\
                        f'df_{tau}.loc[year,\'Non-college Employment Rate (Head Tax)\'])')
            exec(f'chg_empRate_p = (df_{tau}.loc[ref_year,\'Non-college Employment Rate (Payroll Tax)\'] - ' +\
                        f'df_{tau}.loc[year,\'Non-college Employment Rate (Payroll Tax)\'])')
            pct_diff_empRate = 100*((chg_empRate_p - chg_empRate_h) / chg_empRate_h)
            
            '''
            print(f'Had we used a proportional tax from {year}-{ref_year}:')
            print(f'   The college wage premium rise would have been ' +\
                  f'{pct_diff_cwpRatio:.2f}% smaller (+{chg_cwpRatio_p:.2f}, not +{chg_cwpRatio_h:.2f})')
            print(f'   The college wagebill share rise would have been ' +\
                  f'{pct_diff_cswb:.2f}% smaller (+{chg_cswb_p:.2f}, not +{chg_cswb_h:.2f})')
            print(f'   The non-college emp rate rise would have been ' +\
                  f'{pct_diff_empRate:.2f}% bigger (+{chg_empRate_p:.3f}, not +{chg_empRate_h:.3f})')
            
            print()
            print()
            '''
            
            # Collect and Graph outcomes
            outcomes = ['College Wage Premium', 'College Share of Wage Bill', 'Non-college Employment Rate']
            outcomes_h = [chg_cwpRatio_h, chg_cswb_h, chg_empRate_h]
            outcomes_p = [chg_cwpRatio_p, chg_cswb_p, chg_empRate_p]
            width = 0.40
            
            plt.figure(figsize=(9,4))
            x = np.arange(3)
            plt.bar(x-0.2, outcomes_h, width, color='indianred', label="Head Tax")
            plt.bar(x+0.2, outcomes_p, width, color='steelblue', label="Payroll Tax")
            
            # Add Values ot top of bars
            i=0.1
            for value in (outcomes_p + outcomes_h):
                if value >= 0: placement = value+0.003
                elif value < 0: placement = value-0.006
                plt.text(i, placement, s=f'{value:.3f}')
                
                if i==2.1: i = i - 2.4
                else: i = i+1
                
            # Format plots
            plt.xticks(x, outcomes, fontsize=11.5)
            plt.axhline(y=0, color='black', lw=1)
            plt.legend()
            plt.ylabel("Change in Levels over Time", fontsize=13)
            if not any([x < 0 for x in (outcomes_h + outcomes_p)]):
                plt.gca().set_ylim(bottom=-0.02)
            plt.title(f'Change from {year} to {ref_year} under ESHI Financing Counterfactual', y=1.01, fontsize=15)
            plt.grid(color='gainsboro')
            plt.figtext(0.1, 0.01, f"Note: Policy counterfactual calculates cost of ESHI based on the {tau2specification_Dict[tau].lower()}", \
                        ha="left", fontsize=8.5, bbox={"facecolor":"white", "alpha":0.5, "pad":5})
            plt.savefig(f'CounterfactualGrowth_{year}_{tau}.png', dpi=500)
            plt.clf() 