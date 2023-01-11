#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 19:14:35 2022
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
from fzz_calibration import calibration_model


#%%      Establishing Baseline Parameters      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('RC1_observed_data.csv', index_col=0)

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


#%%      Construct Results by Varying Tau      %%#
#Parameters to be varied:
tau_params = ['tau_baseline', 'tau_high']

#Calculate Observed Change over Time
chg_w_C_observed = df_observed.loc[year2, 'wage1_c']-df_observed.loc[year1, 'wage1_c']
chg_w_N_observed = df_observed.loc[year2, 'wage1_n']-df_observed.loc[year1, 'wage1_n']
chg_cwp_observed = 100*((df_observed.loc[year2, 'wage1_c']/df_observed.loc[year2, 'wage1_n'])\
               -(df_observed.loc[year1, 'wage1_c']/df_observed.loc[year1, 'wage1_n']))

chg_P_C_observed = 100*(df_observed.loc[year2, 'P1_c']-df_observed.loc[year1, 'P1_c'])
chg_P_N_observed = 100*(df_observed.loc[year2, 'P1_n']-df_observed.loc[year1, 'P1_n'])

chg_employment_C_observed = ((df_observed.loc[year2, 'pop_count']*df_observed.loc[year2,'share_pop_c']*df_observed.loc[year2, 'P1_c']) - \
                                (df_observed.loc[year1, 'pop_count']*df_observed.loc[year1,'share_pop_c']*df_observed.loc[year1, 'P1_c']))\
                                /1e6
chg_employment_N_observed = ((df_observed.loc[year2, 'pop_count']*(1-df_observed.loc[year2,'share_pop_c'])*df_observed.loc[year2, 'P1_n']) - \
                                (df_observed.loc[year1, 'pop_count']*(1-df_observed.loc[year1,'share_pop_c'])*df_observed.loc[year1, 'P1_n']))\
                                /1e6
chg_employment_observed = chg_employment_C_observed + chg_employment_N_observed

chg_cwb_observed = 100*(((df_observed.loc[year2,'share_pop_c']*df_observed.loc[year2, 'P1_c']*df_observed.loc[year2, 'wage1_c'])/\
                    (df_observed.loc[year2,'share_pop_c']*df_observed.loc[year2, 'P1_c']*df_observed.loc[year2, 'wage1_c'] \
                     + (1-df_observed.loc[year2,'share_pop_c'])*df_observed.loc[year2,'P1_n']*df_observed.loc[year2, 'wage1_n']))\
               -((df_observed.loc[year1,'share_pop_c']*df_observed.loc[year1, 'P1_c']*df_observed.loc[year1, 'wage1_c'])/\
                    (df_observed.loc[year1,'share_pop_c']*df_observed.loc[year1, 'P1_c']*df_observed.loc[year1, 'wage1_c'] \
                     + (1-df_observed.loc[year1,'share_pop_c'])*df_observed.loc[year1,'P1_n']*df_observed.loc[year1, 'wage1_n'])))

### Initialize strings
chg_tau_string = '\\ \\ Change in Cost  $(\\tau_{2019}-\\tau_{1977})$ \n \t & - '
chg_t_string = '\\ \\ Payroll Tax $(t_{2019}-t_{1977})$ \n \t & - '
chg_w_C_string = '\\ \\ Change in College Wages $w_{C,2019}-w_{C,1977}$ \n \t '+f'& \${chg_w_C_observed:,.0f}'
chg_w_N_string = '\\ \\ Change in Non-college Wages $w_{N,2019}-w_{N,1977}$ \n \t '+f'& \${chg_w_N_observed:,.0f}'
chg_cwp_string = '\\ \\ PP Change in College Wage Premium \n \t '+f'& {chg_cwp_observed:,.2f} pp'
chg_P_c_string = '\\ \\ \\small Change in College Employment Rate $P_{C,2019}-P_{C,1977}$ \n \t '+f'& {chg_P_C_observed:,.2f} pp'
chg_P_n_string = '\\ \\ \\small Change in Non-college Employment Rate $P_{N,2019}-P_{N,1977}$ \n \t '+f'& {chg_P_N_observed:,.2f} pp'
chg_employment_string = r'\underline{Total Employment (\textit{M}):}' +f' \n \t & {chg_employment_observed:,.2f}'
chg_employment_C_string = f'\\ \\ \\small College \n \t & {chg_employment_C_observed:,.2f}'
chg_employment_N_string = f'\\ \\ \\small Non-College \n \t & {chg_employment_N_observed:,.2f}'
chg_cwb_string = f'\\ \\ College Share of the Wage Bill \n \t & {chg_cwb_observed:,.2f} pp'

### Loop through different tau parameters
i = 0
for tau_param in tau_params:
    i = i+1
    
    #Define Model
    model_year1 = calibration_model(alpha_c, alpha_n,
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
    
    model_year2 = calibration_model(alpha_c, alpha_n,
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
    
    #Add values to strings for Eq Comparison Table
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'

    #Calculate Results
    chg_tau = model_year2.tau-model_year1.tau
    chg_t = 100*(model_year2.t-model_year1.t)
    chg_w_C = model_year2.w2_c-model_year1.w2_c
    chg_w_N = model_year2.w2_n-model_year1.w2_n
    chg_cwp = 100*((model_year2.w2_c/model_year2.w2_n)-(model_year1.w2_c/model_year1.w2_n))
    chg_P_C = 100*(model_year2.P2_c-model_year1.P2_c)
    chg_P_N = 100*(model_year2.P2_n-model_year1.P2_n)
    chg_employment = (model_year2.employment2-model_year1.employment2)/1e6
    chg_employment_C = (model_year2.employment2_c-model_year1.employment2_c)/1e6
    chg_employment_N = (model_year2.employment2_n-model_year1.employment2_n)/1e6
    chg_cwb = 100*(((model_year2.L2_c*model_year2.w2_c)/(model_year2.L2_c*model_year2.w2_c + model_year2.L2_n*model_year2.w2_n))\
                   -((model_year1.L2_c*model_year1.w2_c)/(model_year1.L2_c*model_year1.w2_c + model_year1.L2_n*model_year1.w2_n)))
        
    #Save Results
    chg_tau_string = chg_tau_string + f' && \${chg_tau:,.0f} '
    chg_t_string = chg_t_string + f' && {chg_t:,.2f} pp '
    chg_w_C_string = chg_w_C_string + f' && \${chg_w_C:,.0f} '
    chg_w_N_string = chg_w_N_string + f' && \${chg_w_N:,.0f} '
    chg_cwp_string = chg_cwp_string + f' && {chg_cwp:,.2f} pp '
    
    chg_P_c_string = chg_P_c_string + f' && {chg_P_C:,.2f} pp '
    chg_P_n_string = chg_P_n_string + f' && {chg_P_N:,.2f} pp '
    chg_employment_string = chg_employment_string + f' && {chg_employment:,.2f} '
    chg_employment_C_string = chg_employment_C_string + f' && {chg_employment_C:,.2f} '
    chg_employment_N_string = chg_employment_N_string + f' && {chg_employment_N:,.2f} '
    
    chg_cwb_string = chg_cwb_string + f' && {chg_cwb:,.2f} pp'
    
    
#%%      Compile and Export LaTeX file:      %%#
## LaTeX code for header
header = ['\\begin{tabular}{lccccc}', '\n',
          '\\FL', '\n',
          '\t & && \multicolumn{3}{c}{Payroll Tax Equilibrium} \\\\', '\n',
          '\cmidrule{4-6} \n',
          '\t &	 \multicolumn{1}{p{2.2cm}}{\centering Head Tax \ Equilibrium}','\n', 
          '\t &&	 \multicolumn{1}{p{2.4cm}}{\centering Baseline}','\n', 
          '\t &&	 \multicolumn{1}{p{2.4cm}}{\centering  Full Coverage}', '\\\\','\n', 
          '\cmidrule{1-6}', '\n']

## LaTeX code for table results
table_values=['\\underline{Employer-Sponsored Health Insurance:}', ' \\\\\n', 
              chg_tau_string, ' \\\\\n',
              chg_t_string, ' \\\\\n',
              '\\\\\n',
              '\\underline{Wages:}', ' \\\\\n', 
              chg_w_C_string, ' \\\\\n',
              chg_w_N_string, ' \\\\\n',
              chg_cwp_string, ' \\\\\n',
              '\\ \\ ${(w_c/w_N - 1)}_{2019}-{(w_c/w_N - 1)}_{1977}$', ' \\\\\n',
              '\\\\\n',
              '\\underline{Employment Rate:}', ' \\\\\n',
              chg_P_c_string, ' \\\\\n',
              chg_P_n_string, ' \\\\\n',
              '\\\\\n',
              '\\underline{Wage Bill:}', ' \\\\\n',
              chg_cwb_string,' \\\\\n',
              '\\ \\ ${\\left(\\frac{w_C L_C}{w_N L_N + w_C L_C}\\right)}_{2019}-{\\left(\\frac{w_C L_C}{w_N L_N + w_C L_C}\\right)}_{1977}$', ' \\\\\n']

## LaTeX code for closer
closer = ['\\bottomrule','\n', '\end{tabular}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"RC1_CounterfactualGrowth.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()