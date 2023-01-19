#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 20:34:11 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
graph_output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/RC3_CESLD'
table_output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/RC3_CESLD'

### Import calibration class
os.chdir(code_folder)
#from fzz_calibration import calibration_model 
from fzz_calibration_RC3_CESLD import calibration_model_RC3 



#%% Tables: Varying Rho for 2019 #%% 
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

#Initialize strings for tables
column_header_string = ''
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
delta_cwp_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'

# Parameter assumptions:
alpha_c=1
alpha_n=1
tau_param = 'tau_high'
year = 2019

# Parameter to be varied:
rho_values = [1, 0.3827, 0.01, -0.33, -10]

# Loop through rho values in calibration process
i = 0
for rho_value in rho_values:
    i = i+1
    
    #Define and calibrate model
    model = calibration_model_RC3(alpha_c, alpha_n,
                rho=rho_value,
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
    
    #Calibrate Model
    model.calibrate()
    
    #Output Summary tables
    model.generate_table(file_name='SummaryTable'+str(year)+f"_RC3_rho{i}", year=year, 
                     table_type="equilibrium summary",
                     table_label="SummaryTable"+str(year)+f"-RC3-rho{i}", 
                     location=table_output_path, 
                     subtitle=f" with $\\rho = {str(rho_value)}$")

    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small $\\rho = {str(rho_value)}$ \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
    delta_cwp_string = delta_cwp_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
    
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

header = [f'\ctable[caption={{Equilibrium Comparison for {year} Across Substitutability ($\\rho$) }},', '\n',
          '    label={EqComparison_AcrossRho}, pos=h!]', '\n',
          '{lccccccccc}{}{\\FL', '\n',
          column_header_string, '\\\\',
          '\cmidrule{1-10}', '\n']            

table_values=['\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                delta_cwp_string, ' \\\\\n',
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
os.chdir(table_output_path)
file = open("EqComparison_AcrossRho.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()


#%%  Graphs: Varying Rho Over Time #%% 
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
tau_param = 'tau_high'

# Parameter to be varied:
years = [1977,1987] + list(range(1996, 2020))
rho_values = [1, 0.3827, 0.01, -0.33, -10]

#Loop through values of tau and year
df_varying_rho_byYear = pd.DataFrame(
    columns = ['year', 'Substitutability', 
               "Pct. Chg. in College Wage Premium (H to P)", 
               "Change in College Share of Wage Bill (H to P)"])

# Loop through rho pairs in calibration process
for rho_value in rho_values:
    
    for year in years:
        #Define and calibrate model
        model = calibration_model_RC3(alpha_c, alpha_n,
                    rho=rho_value,
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
        
        #Calibrate Model
        model.calibrate()

        #Calculate variables of interest
        pct_chg_wage_premium_12 = -1*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
        pp_chg_wage_bill_12 = -100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))

        #Create rows for dataframe and append them
        new_row = {'year':year, 'Substitutability':rho_value, \
                      "Pct. Chg. in College Wage Premium (H to P)":pct_chg_wage_premium_12, 
                      "Change in College Share of Wage Bill (H to P)":pp_chg_wage_bill_12}

        df_varying_rho_byYear = df_varying_rho_byYear.append(new_row, ignore_index=True)


#Generate Tables
os.chdir(graph_output_path)
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False

params2colors_Dict={str(1):"navy",
                    str(0.3827):'steelblue',
                    str(0.01):"slategrey", 
                    str(-0.33):"indianred",
                    str(-10):"maroon"}

legend_labels = ['Perfect Substitutes',
                 'Gross Substitutes',
                 'Cobb-Douglas',
                 'Gross Complements',
                 'Strong Complements']

#Pct. Chg. Reduction in College Wage Premium
plt.figure(figsize=(6,4))
for rho_value in rho_values:
    df_series = df_varying_rho_byYear[[x == rho_value \
                        for x in df_varying_rho_byYear['Substitutability']]]
    plt.plot(df_series['year'], df_series["Pct. Chg. in College Wage Premium (H to P)"],\
             label=str(rho_value),
             color=params2colors_Dict[str(rho_value)])
plt.legend(legend_labels)
plt.xlabel("Year")
plt.ylabel("Pct. Reduction in College Wage Premium")
plt.grid(axis='y', color='gainsboro')
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0%}'))
plt.grid(axis='y', color='gainsboro')
plt.savefig('varyRho_overTime_cwp.png', dpi=500)
plt.clf()
   
#PP Reduction in College Wage Premium  
plt.figure(figsize=(6,4))
for rho_value in rho_values: 
    df_series = df_varying_rho_byYear[[x == rho_value \
                        for x in df_varying_rho_byYear['Substitutability']]]
    plt.plot(df_series['year'], df_series["Change in College Share of Wage Bill (H to P)"],\
             label=str(rho_value),
             color=params2colors_Dict[str(rho_value)])
plt.legend(legend_labels)
plt.xlabel("Year")
plt.ylabel("PP. Reduction in College Wage Bill")
plt.grid(axis='y', color='gainsboro')
plt.savefig('varyRho_overTime_cwb.png', dpi=500)
plt.clf()