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
output_folder = main_folder +"/output/Tables/Time Varying Tau"
os.chdir(code_folder)

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model 


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
                'tau_baseline': premium_data['Avg Enr Cost']*ASEC_data['Share ESHI policyholders (weighted)'].backfill(), #Added for this Appendix,
                'tau_low': premium_data['Avg Emp Cost']**ASEC_data['Share ESHI policyholders (weighted)'].backfill(),
                'Share ESHI policyholders':ASEC_data['Share ESHI policyholders (weighted)'],
                'Share ESHI policyholders, College':ASEC_data['Share ESHI policyholders, College (weighted)'],
                'Share ESHI policyholders, Non-college':ASEC_data['Share ESHI policyholders, Non-college (weighted)']
            })


#%%  Table 5: Counterfactual Growth Across Tau #%%  

####   Parameter assumptions:
alpha_c=1
alpha_n=1
year1 = 1977
year2 = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


####  Calibration while Varying Tau

#Parameters to be varied:
#tau_params = ['tau_high', 'tau_baseline', 'tau_low']
tau_params = ['tau_baseline', 'tau_high']
tau2specification_Dict ={'tau_high':'Total Cost with Complete Takeup',
                         'tau_baseline':'Total Cost with Incomplete Takeup',
                         'tau_low':'Cost to Employer with Incomplete Takeup'}

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
# Growth over Time
chg_tau_string = f'\\ \\ Cost $(\\tau)$ \n \t & - '
chg_t_string = f'\\ \\ Payroll Tax $(t)$ \n \t & - '
chg_w_C_string = f'\\ \\ $w_C$ \n \t & \${chg_w_C_observed:,.0f}'
chg_w_N_string = f'\\ \\ $w_N$ \n \t & \${chg_w_N_observed:,.0f}'
chg_cwp_string = f'\\ \\ $w_C/w_N - 1$ \n \t & {chg_cwp_observed:,.2f} pp'
chg_P_c_string = f'\\ \\ \\small College \n \t & {chg_P_C_observed:,.2f} pp'
chg_P_n_string = f'\\ \\ \\small Non-College \n \t & {chg_P_N_observed:,.2f} pp'
chg_employment_string = r'\underline{Total Employment (\textit{M}):}' +f' \n \t & {chg_employment_observed:,.2f}'
chg_employment_C_string = f'\\ \\ \\small College \n \t & {chg_employment_C_observed:,.2f}'
chg_employment_N_string = f'\\ \\ \\small Non-College \n \t & {chg_employment_N_observed:,.2f}'
chg_cwb_string = f'\\ \\ College Share: \n \t & {chg_cwb_observed:,.2f} pp'

# Difference over Time
CG_chg_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
CG_chg_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
CG_chg_cwp_string = '\\ \\ $\Delta(w_C/w_N - 1)$ \n \t'
CG_chg_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
CG_chg_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
CG_chg_cwb_string = '$\\ \\ \\Delta$(\\small College Share): \n \t'


#Loop through different tau parameters
i = 0
for tau_param in tau_params:
    i = i+1
    label = tau2specification_Dict[tau_param]
    
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
    
    print(model_year1.tau)
    print(model_year2.tau)
    
    #Add values to strings for Eq Comparison Table
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'

    #Calculate Change over Time in Payroll Tax counterfactual
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
                   -((model_year1.L2_c*model_year1.w2_c)/(model_year1.L2_c*model_year1.w2_c + model_year1.L2_n*model_year1.w1_n)))
    
    #Calculate Change relative to Head Tax
    CG_chg_w_C = chg_w_C - chg_w_C_observed
    CG_chg_w_N = chg_w_N - chg_w_N_observed
    CG_chg_cwp = chg_cwp - chg_cwp_observed
    CG_chg_P_C = chg_P_C - chg_P_C_observed
    CG_chg_P_N = chg_P_N - chg_P_N_observed
    CG_chg_cwb = chg_cwb - chg_cwb_observed
    
    ## Add Values to Strings
    # Change over time
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
    
    # Difference in Counterfactuals
    CG_chg_w_C_string = CG_chg_w_C_string + ampersand + f' \${CG_chg_w_C:,.0f} '
    CG_chg_w_N_string = CG_chg_w_N_string + ampersand + f' \${CG_chg_w_N:,.0f} '
    CG_chg_cwp_string = CG_chg_cwp_string + ampersand + f' {CG_chg_cwp:,.2f} pp '
    
    CG_chg_P_c_string = CG_chg_P_c_string + ampersand + f' {CG_chg_P_C:,.2f} pp '
    CG_chg_P_n_string = CG_chg_P_n_string + ampersand + f' {CG_chg_P_N:,.2f} pp '
    
    CG_chg_cwb_string = CG_chg_cwb_string + ampersand + f' {CG_chg_cwb:,.2f} pp'
    
    
####  Creating Tables
    
    
## Growth over Time 
header = ['\\begin{tabular}{lccccc}', '\n',
          '\\FL', '\n',
          '\t & && \multicolumn{3}{c}{Payroll Tax Equilibrium} \\\\', '\n',
          '\cmidrule{4-6} \n',
          '\t &	 \multicolumn{1}{p{2.2cm}}{\centering Head Tax \ Equilibrium}','\n', 
          '\t &&	 \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering \\textbf{Baseline}}','\n', 
          '\t &&	 \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering  Total Cost, \\\\ FTFY Workers}', '\\\\','\n', 
          '\cmidrule{1-6}', '\n']

table_values=['\\underline{ESHI:}', ' \\\\\n', 
              chg_tau_string, ' \\\\\n',
              chg_t_string, ' \\\\\n',
              '\\\\\n',
              '\\underline{Wages:}', ' \\\\\n', 
              chg_w_C_string, ' \\\\\n',
              chg_w_N_string, ' \\\\\n',
              chg_cwp_string, ' \\\\\n',
              '\\\\\n',
              '\\underline{Employment Rate:}', ' \\\\\n',
              chg_P_c_string, ' \\\\\n',
              chg_P_n_string, ' \\\\\n',
              '\\\\\n',
              #chg_employment_string, ' \\\\\n',
              #chg_employment_C_string, ' \\\\\n',
              #chg_employment_N_string, ' \\\\\n',
              #'\\\\\n',
              '\\underline{Wage Bill:}', ' \\\\\n',
              chg_cwb_string,' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"TVT_Change_OverTime{year2}_{year1}_ByTau.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()

## Difference in Counterfactual Growth
header = ['\\begin{tabular}{lccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering \\textbf{Baseline}}','\n', 
          '\t &&	 \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering  Total Cost, \\\\ FTFY Workers}', '\\\\','\n', 
          '\cmidrule{1-4}', '\n']

table_values=['\\underline{Wages:}', ' \\\\\n',
                CG_chg_w_C_string, ' \\\\\n',
                CG_chg_w_N_string, ' \\\\\n',
                CG_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment Rate:}', ' \\\\\n',
                CG_chg_P_c_string, ' \\\\\n',
                CG_chg_P_n_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                CG_chg_cwb_string,' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']
#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"TVT_Diff_Change_OverTime{year2}_{year1}_ByTau.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()

