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


#%%  Calibration Across Tau #%% 
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
                         location=output_path, subtitle=f' with {tau2specification_Dict[tau_param]}')
    
    model.generate_table(file_name='EqComparison'+str(year)+"_"+str(tau_param), year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"_"+str(tau_param), 
                     location=output_path, subtitle=f' with {tau2specification_Dict[tau_param]}')
    
    #Create list with comparison table values for this section
    table_values_section = [f'\\underline{{ {tau2specification_Dict[tau_param]} }} \\\\', '\n',
    f'\\ \\ \\small Pct. Chg. in College Wage Premium',
        f' & {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\%',
        ' \\\\\n',
    f'\\ \\ \\small Change in College Share of Wage Bill', 
        f' & {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp',
        ' \\\\\n',
    f'\\ \\ \\small Change in College Share of Workforce', 
        f' & {100*(((model.L2_c)/(model.L2_c + model.L2_n))-((model.L1_c)/(model.L1_c + model.L1_n))):,.2f} pp',
        ' \\\\\n',
        '\\\\\n']
    #Append this to the existing list
    comparison_table_values.extend(table_values_section)

#Generate header and close 
header = [f'\ctable[caption={{Calibration Results Across $\\tau$ for {year} }},', '\n',
        f'    label=ResultsAcrossTau{year}, pos=h!]', '\n',
        '{lc}{',
            '$^{*}$& The values of $\\tau$: ',  '\n',
            f'    (1) Total Cost and Complete Take-up: \\${df_observed.loc[year, tau_params[0]]:,.0f}; ',  '\n',
            f'    (2) Cost to Employer and Complete Take-up: \\${df_observed.loc[year, tau_params[1]]:,.0f}; ',  '\n',
            f'    (3) Cost to Employer and Incomplete Take-up: \\${df_observed.loc[year, tau_params[2]]:,.0f}. \\N',  '\n',
        '}{\\FL', '\n',
        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
        '\\cmidrule{1-2}', '\n']

closer = ['\\bottomrule}']

cwd = os.getcwd()
os.chdir(output_path)
file = open("Results_across_tau_"+str(year)+".tex","w")
file.writelines(header) 
file.writelines(comparison_table_values)   
file.writelines(closer)   
file.close()
os.chdir(cwd)


#%%  Contribution of ESHI to College Wage Premium over Time and across Tau #%%
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
                         'tau_med':'Cost to Employer and Complete Take-up',
                         'tau_low':'Cost to Employer and Incomplete Take-up'}

#Output path 
output_path = '/Users/caseymcquillan/Desktop/'

#Loop through values of tau and year
df_outcomes = pd.DataFrame(columns = ['year', 'Tau',
                    "College Wage Premium (Head Tax)",
                    "College Wage Premium (Payroll Tax)",
                    "College Share of the Wage Bill (Head Tax)",
                    "College Share of the Wage Bill (Payroll Tax)",
                    "Non-college Employment Rate (Head Tax)", 
                    "Non-college Employment Rate (Payroll Tax) "])

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
                    "Non-college Employment Rate (Head Tax)": model.P1_n, \
                    "Non-college Employment Rate (Payroll Tax)": model.P2_n}
        df_outcomes = df_outcomes.append(\
                    [new_row], ignore_index=True)
#Set year as index
df_outcomes=df_outcomes.set_index('year')   

#Create subsets based on college definition
for tau in tau_params:
    exec(f'df_{tau} = df_outcomes[df_outcomes[\'Tau\']==\'{tau}\']') 

# Had we used a payroll tax from 1987-2019:
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
    
            print(f'Had we used a proportional tax from {year}-{ref_year}:')
            print(f'   The college wage premium rise would have been ' +\
                  f'{pct_diff_cwpRatio:.2f}% smaller (+{chg_cwpRatio_p:.2f}, not +{chg_cwpRatio_h:.2f})')
            print(f'   The college wagebill share rise would have been ' +\
                  f'{pct_diff_cswb:.2f}% smaller (+{chg_cswb_p:.2f}, not +{chg_cswb_h:.2f})')
            print(f'   The non-college emp rate rise would have been ' +\
                  f'{pct_diff_empRate:.2f}% bigger (+{chg_empRate_p:.3f}, not +{chg_empRate_h:.3f})')
            
            print()
        print()
    
    
    