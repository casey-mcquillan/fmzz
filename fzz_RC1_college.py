#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 21:48:29 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
#Import Packages
import os as os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model 


#%% 1a. Cleaning ASEC Data #%%
#Import Data
os.chdir(data_folder)
df = pd.read_csv('cps_00011.csv')

# Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]
df = df[df['CLASSWLY']!=99]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

# Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

### Define college attendance
#College Definition 1
df['College (Definition 1)'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College (Definition 1)'] = 1- df['College (Definition 1)'] 

#College Definition 2
df['College (Definition 2)'] = \
    [int(x in [90, 100, 110, 120, 121, 122, 91, 92, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College (Definition 2)'] = 1- df['College (Definition 2)'] 

#College Definition 3
df['College (Definition 3)'] = \
    [int(x in [80, 90, 100, 110, 120, 121, 122, 81, 91, 92, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College (Definition 3)'] = 1- df['College (Definition 3)'] 

# Define working
hours_requirment =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirment =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirment * weeks_requirment

# Define Health Insurance
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
''' Other variables with different time inconsistencies
df['HI'] = 1*(df['ANYCOVLY']==2 or df['VERIFY']==2)
df['ESHI'] =   1*(df['GRPCOVLY']==2 or df['INCLUGH']==2)
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']
'''

# Constant column
df['Total'] = 1

    
#%% 1b. Data Collapse #%%

# Define range of years
years = range(1975,2021)

# Define variables
variables = ['N', 'N_FTFY',
                    'Share ESHI policyholders', 
                    'Share ESHI policyholders (weighted)']
for def_num in [1,2,3]:
    variables = variables + [f'N_college [College Definition {def_num}]', 
                f'N_college_FTFY [College Definition {def_num}]',
                f'share_pop_c [College Definition {def_num}]',
                f'share_pop_c (weighted) [College Definition {def_num}]',
                f'share_workers1_c [College Definition {def_num}]', 
                f'share_workers1_c (weighted) [College Definition {def_num}]',
                f'P1_c [College Definition {def_num}]',
                f'P1_c (weighted) [College Definition {def_num}]',
                f'P1_n [College Definition {def_num}]',
                f'P1_n (weighted) [College Definition {def_num}]',
                f'wage1_c [College Definition {def_num}]',
                f'wage1_c (weighted) [College Definition {def_num}]',
                f'wage1_n [College Definition {def_num}]',
                f'wage1_n (weighted) [College Definition {def_num}]']

# Create dataframe
data = pd.DataFrame(index=years, columns=variables)

# Loop through years to create dataframe
for year in years:
    year_dummy = 1*(df['YEAR']==year)
        
    ### Calculations unrelated to College Definition
    data.loc[year,'N'] = np.sum(df['Total']*year_dummy)
    data.loc[year,'N_FTFY'] = np.sum(df['FTFY']*year_dummy)
    
    ## Share of FTFY workers that are ESHI policyholders
    if year >= 1995:
        data.loc[year,'Share ESHI policyholders'] = \
            np.average(df['ESHI_own']*df['FTFY'], \
                       weights=year_dummy*df['FTFY'])
        data.loc[year,'Share ESHI policyholders (weighted)'] = \
            np.average(df['ESHI_own']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df['FTFY'])   
    
    ### Calculations unrelated to College Definition
    for def_num in ['1', '2', '3']:
        ## Number of observations
        data.loc[year,f'N_college [College Definition {def_num}]'] = np.sum(df[f'College (Definition {def_num})']*year_dummy)
        data.loc[year,f'N_college_FTFY [College Definition {def_num}]'] = np.sum(df[f'College (Definition {def_num})']*df['FTFY']*year_dummy)
        
        ## College Share of population
        data.loc[year,f'share_pop_c [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})'], \
                       weights=year_dummy)
        data.loc[year,f'share_pop_c (weighted) [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})'], \
                       weights=df['ASECWT']*year_dummy)
        
        ## College Share of FTFY workforce
        data.loc[year,f'share_workers1_c [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})']*df['FTFY'], \
                       weights=year_dummy*df['FTFY'])
        data.loc[year,f'share_workers1_c (weighted) [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})']*df['FTFY'], 
                       weights=df['ASECWT']*year_dummy*df['FTFY'])
        ## Employment Rates
        data.loc[year,f'P1_c [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})']*df['FTFY'], \
                       weights=year_dummy*df[f'College (Definition {def_num})'])
        data.loc[year,f'P1_c (weighted) [College Definition {def_num}]'] = \
            np.average(df[f'College (Definition {def_num})']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df[f'College (Definition {def_num})'])
        
        data.loc[year,f'P1_n [College Definition {def_num}]'] = \
            np.average(df[f'Non-College (Definition {def_num})']*df['FTFY'], \
                       weights=year_dummy*df[f'Non-College (Definition {def_num})'])
        data.loc[year,f'P1_n (weighted) [College Definition {def_num}]'] = \
            np.average(df[f'Non-College (Definition {def_num})']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df[f'Non-College (Definition {def_num})'])
    
        ## Wage Data
        data.loc[year,f'wage1_c [College Definition {def_num}]'] = \
            np.average(df['INCWAGE']*df[f'College (Definition {def_num})']*df['FTFY'], \
                       weights=year_dummy*df[f'College (Definition {def_num})']*df['FTFY'])
        data.loc[year,f'wage1_c (weighted) [College Definition {def_num}]'] = \
            np.average(df['INCWAGE']*df[f'College (Definition {def_num})']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df[f'College (Definition {def_num})']*df['FTFY'])
        data.loc[year,f'wage1_n [College Definition {def_num}]'] = \
            np.average(df['INCWAGE']*df[f'Non-College (Definition {def_num})']*df['FTFY'], \
                       weights=year_dummy*df[f'Non-College (Definition {def_num})']*df['FTFY'])
        data.loc[year,f'wage1_n (weighted) [College Definition {def_num}]'] = \
            np.average(df['INCWAGE']*df[f'Non-College (Definition {def_num})']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df[f'Non-College (Definition {def_num})']*df['FTFY'])


#%% Inflation Adjust #%%
# Adjust wages to be in 2019 dollars
os.chdir(data_folder)
price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
for year in data.index:
    adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
    for def_num in [1,2,3]:
        for var in [f'wage1_c [College Definition {def_num}]', 
                    f'wage1_n [College Definition {def_num}]', 
                    f'wage1_c (weighted) [College Definition {def_num}]', 
                    f'wage1_n (weighted) [College Definition {def_num}]']:
            data.loc[year, var] = adj_factor*data.loc[year, var]        
        
        
#%% 1c. Export Data #%%
os.chdir(data_folder)

# Define variables
variables = ['N', 'N_FTFY',
                    'Share ESHI policyholders', 
                    'Share ESHI policyholders (weighted)']
for def_num in [1,2,3]:
    variables = variables + [f'N_college [College Definition {def_num}]', 
                f'N_college_FTFY [College Definition {def_num}]',
                f'share_pop_c [College Definition {def_num}]',
                f'share_pop_c (weighted) [College Definition {def_num}]',
                f'share_workers1_c [College Definition {def_num}]', 
                f'share_workers1_c (weighted) [College Definition {def_num}]',
                f'P1_c [College Definition {def_num}]',
                f'P1_c (weighted) [College Definition {def_num}]',
                f'P1_n [College Definition {def_num}]',
                f'P1_n (weighted) [College Definition {def_num}]',
                f'wage1_c [College Definition {def_num}]',
                f'wage1_c (weighted) [College Definition {def_num}]',
                f'wage1_n [College Definition {def_num}]',
                f'wage1_n (weighted) [College Definition {def_num}]']

#Export
data_export = data[variables]
data_export.to_csv('CPS_ASEC_clean_RC1.csv')


#%%  2. Compiling Obsereved Data and Exporting #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('CPS_ASEC_clean_RC1.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Emily")
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)

# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'epop_ratio': OECD_data['Employment Rate (25-64)']/100,
                'pop_count': OECD_data['Population (25-64)'],
                'tau_high': premium_data['Avg Enr Cost'],
                'tau_baseline': premium_data['Avg Enr Cost']*ASEC_data['Share ESHI policyholders (weighted)'],
                'tau_low': premium_data['Avg Emp Cost']*ASEC_data['Share ESHI policyholders (weighted)']})
                
for def_num in [1,2,3]:              
    df_observed[f'share_pop_c [College Definition {def_num}]'] = ASEC_data[f'share_pop_c (weighted) [College Definition {def_num}]']
    df_observed[f'share_workers1_c [College Definition {def_num}]'] = ASEC_data[f'share_workers1_c (weighted) [College Definition {def_num}]']
    df_observed[f'wage1_c [College Definition {def_num}]'] = ASEC_data[f'wage1_c (weighted) [College Definition {def_num}]']
    df_observed[f'wage1_n [College Definition {def_num}]'] = ASEC_data[f'wage1_n (weighted) [College Definition {def_num}]']
    df_observed[f'P1_c [College Definition {def_num}]'] = ASEC_data[f'P1_c (weighted) [College Definition {def_num}]']
    df_observed[f'P1_n [College Definition {def_num}]'] = ASEC_data[f'P1_n (weighted) [College Definition {def_num}]']

## Select relevant variables
data_export = df_observed

## Export data
os.chdir(data_folder)
data_export.to_csv('observed_data_RC1.csv')


#%%  3. Figures #%%
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_RC1.csv', index_col=0)

#Define variables and plot titles
variables = ['share_pop_c', 'share_workers1_c',
             'wage1_c', 'wage1_n',
             'P1_c', 'P1_n']
variables2name_dict = {'share_pop_c':'Share of Population with College Education', 
                        'share_workers1_c':'Share of Workforce with College Education',
                        'wage1_c':'College Wages', 
                        'wage1_n':'Non-college Wages',
                        'P1_c':'College Employment Rate', 
                        'P1_n':'Non-college Remployment Rate'}

### Generate Figures
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/RC1_college'
os.chdir(output_path)

for var in variables:
    plot_title = variables2name_dict[var]
    for def_num in [1,2,3]:
        plt.plot(df_observed[f'{var} [College Definition {def_num}]'], label=f'College Definition {def_num}')
    plt.legend()
    plt.title(plot_title, fontsize=14)
    plt.savefig(f'{var}_RC1.png', dpi=500)
    plt.clf()
    
for def_num in [1,2,3]:
    plt.plot(df_observed[f'wage1_c [College Definition {def_num}]']\
             -df_observed[f'wage1_n [College Definition {def_num}]'],\
            label=f'College Definition {def_num}')
plt.legend()
plt.title("College Wage Premium", fontsize=14)
plt.savefig('college_wage_premium_RC1.png', dpi=500)
plt.clf()

os.chdir(code_folder)

#%%  4. Results Across College Definition #%%
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_RC1.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]

#Output path and define years
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/RC1_college'

#Create list for table values specific to each value of tau
comparison_table_values = []

#Loop through College Definitions
for def_num in [1,2,3]:       
    ## Define and calibrate model    
    model = calibration_model(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c=df_observed.loc[year, f'wage1_c [College Definition {def_num}]'], 
                    w1_n=df_observed.loc[year, f'wage1_n [College Definition {def_num}]'],
                    P1_c=df_observed.loc[year, f'P1_c [College Definition {def_num}]'], 
                    P1_n=df_observed.loc[year, f'P1_n [College Definition {def_num}]'],
                    share_workers1_c=df_observed.loc[year, f'share_workers1_c [College Definition {def_num}]'],
                    share_pop_c=df_observed.loc[year, f'share_pop_c [College Definition {def_num}]'],
                    pop_count=df_observed.loc[year, 'pop_count'])
    
    ##  Make sure there are no NANs in model before calibration
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
    model.generate_table(file_name='SummaryTable'+str(year)+"college"+str(def_num), year=year, 
                         table_type="equilibrium summary", 
                         table_label="SummaryTable"+str(year)+"college"+str(def_num), 
                         location=output_path, subtitle=f' with College Definition {def_num}')
    
    model.generate_table(file_name='EqComparison'+str(year)+"college"+str(def_num), year=year, 
                     table_type="equilibrium comparison", 
                     table_label="EqComparison"+str(year)+"college"+str(def_num), 
                     location=output_path, subtitle=f' with College Definition {def_num}')
    
    #Create list with comparison table values for this section
    table_values_section = [f'\\underline{{ College Definition {def_num} }} \\\\', '\n',
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

#Generate header and closer
header = [f'\ctable[caption={{Calibration Results Across College Definition for {year} }},', '\n',
        f'    label=ResultsAcrossCollegeDefinition{year}, pos=h!]', '\n',
        '{lc}{}{\\FL', '\n',
        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
        '\\cmidrule{1-2}', '\n']
closer = ['\\bottomrule}']
cwd = os.getcwd()
os.chdir(output_path)
file = open("Results_across_college_"+str(year)+".tex","w")
file.writelines(header) 
file.writelines(comparison_table_values)   
file.writelines(closer)   
file.close()
os.chdir(cwd)


#%%  5. Visualizing Results Across College Definition and Time #%%
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_RC1.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]

# Parameter to be varied:
years = list(range(1996, 2020))
def_num = [1,2,3]

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/RC1_college'

#Define varibables
variables = ["Pct. Chg. in College Wage Premium (O to H)", 
             "Pct. Chg. in College Wage Premium (H to P)",
             "Chg. in College Wage Premium (H to P)",
             "Change in College Share of Wage Bill  (O to H)",
             "Change in College Share of Wage Bill  (H to P)"]

#Loop through values of tau and year
df_outcomes = pd.DataFrame(columns = ['year', 'College Definition', 'variable', 'value'])

for def_num in [1,2,3]:   
    for year in years:
        ## Define and calibrate model    
        model = calibration_model(alpha_c, alpha_n,
                        rho=rho_baseline,
                        tau=df_observed.loc[year, tau_baseline],
                        elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                        w1_c=df_observed.loc[year, f'wage1_c [College Definition {def_num}]'], 
                        w1_n=df_observed.loc[year, f'wage1_n [College Definition {def_num}]'],
                        P1_c=df_observed.loc[year, f'P1_c [College Definition {def_num}]'], 
                        P1_n=df_observed.loc[year, f'P1_n [College Definition {def_num}]'],
                        share_workers1_c=df_observed.loc[year, f'share_workers1_c [College Definition {def_num}]'],
                        share_pop_c=df_observed.loc[year, f'share_pop_c [College Definition {def_num}]'],
                        pop_count=df_observed.loc[year, 'pop_count'])
        
        ##  Make sure there are no NANs in model before calibration
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

        ## Calibrate Model
        model.calibrate()
    
        ## Calculate variables of interest
        pct_chg_wage_premium_01 = 100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n)
        pct_chg_wage_premium_12 = 100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
        chg_wage_premium_12 = (model.w2_c-model.w2_n)-(model.w1_c-model.w1_n)
        pp_chg_wage_bill_01 = 100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))- \
                                       ((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n)))
        pp_chg_wage_bill_12 = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))

        ## Create rows for dataframe and append them
        new_row1 = {'year':year, 'College Definition':def_num, \
                    'variable':"Pct. Chg. in College Wage Premium (O to H)", \
                    'value':pct_chg_wage_premium_01}    
        new_row2 = {'year':year, 'College Definition':def_num, \
                    'variable':"Pct. Chg. in College Wage Premium (H to P)", \
                    'value':pct_chg_wage_premium_12}
        new_row3 = {'year':year, 'College Definition':def_num, \
                    'variable':"Chg. in College Wage Premium (H to P)", \
                    'value':chg_wage_premium_12}
        new_row4 = {'year':year, 'College Definition':def_num, \
                    'variable':"Change in College Share of Wage Bill  (O to H)", \
                    'value':pp_chg_wage_bill_01}    
        new_row5 = {'year':year, 'College Definition':def_num, \
                    'variable':"Change in College Share of Wage Bill  (H to P)", \
                    'value':pp_chg_wage_bill_12}
        df_outcomes = df_outcomes.append(\
                    [new_row1, new_row2, new_row3, new_row4, new_row5], ignore_index=True)
            
#Generate Graphs
os.chdir(output_path)

for var in variables:
    df_graph = df_outcomes[df_outcomes['variable']==var]

    plt.figure(figsize=(6,4))     
    for def_num in [1,2,3]: 
        df_series = df_graph[[x == def_num for x in df_graph['College Definition']]]
        plt.plot(df_series['year'], df_series['value'], label=f'College Definition {def_num}')
    plt.legend()
    plt.xlabel("Year")
    plt.title(var, fontsize=14)
    if var == "Pct. Chg. in College Wage Premium (O to H)":
        plt.ylim(-1,1)
    plt.savefig('varyCollegeDef_byYear_'+str(variables.index(var) + 1)+'.png', dpi=500)
    plt.clf()  

os.chdir(code_folder)


#%%  6. Contribution of ESHI to College Wage Premium over time #%%
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_RC1.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]

# Parameter to be varied:
years = list(range(1996, 2020))

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/RC1_college'

#Loop through values of tau and year
df_outcomes = pd.DataFrame(columns = ['year', 'College Definition', 
                                      "College Wage Premium", 
                                      "Potential Reduction in College Wage Premium",
                                      "Pct. Reduction in CWP (H to P)"])
for def_num in [1,2,3]:   
    for year in years:
        ## Define and calibrate model    
        model = calibration_model(alpha_c, alpha_n,
                        rho=rho_baseline,
                        tau=df_observed.loc[year, tau_baseline],
                        elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                        w1_c=df_observed.loc[year, f'wage1_c [College Definition {def_num}]'], 
                        w1_n=df_observed.loc[year, f'wage1_n [College Definition {def_num}]'],
                        P1_c=df_observed.loc[year, f'P1_c [College Definition {def_num}]'], 
                        P1_n=df_observed.loc[year, f'P1_n [College Definition {def_num}]'],
                        share_workers1_c=df_observed.loc[year, f'share_workers1_c [College Definition {def_num}]'],
                        share_pop_c=df_observed.loc[year, f'share_pop_c [College Definition {def_num}]'],
                        pop_count=df_observed.loc[year, 'pop_count'])
        
        ##  Make sure there are no NANs in model before calibration
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

        ## Calibrate Model
        model.calibrate()
        
        #Calibrate Model
        model.calibrate()
        
        #Calculate variables of interest
        cwp = model.w1_c - model.w1_n
        contrib_ESHI_cwp = (model.w1_c - model.w1_n) - (model.w2_c - model.w2_n)        
        
        #Create rows for dataframe and append them
        new_row = {'year':year, 'College Definition':def_num, \
                    "College Wage Premium": cwp, \
                    "Potential Reduction in College Wage Premium": contrib_ESHI_cwp,
                    "Pct. Reduction in CWP (H to P)": 100* (contrib_ESHI_cwp/cwp)}    
        df_outcomes = df_outcomes.append(\
                    [new_row], ignore_index=True)
#Set year as index
df_outcomes=df_outcomes.set_index('year')   

#Create subsets based on College Definition
for def_num in [1,2,3]: 
    exec(f'df_outcomes_college{def_num} = df_outcomes[df_outcomes[\'College Definition\']=={def_num}]') 

#Create graphs
os.chdir(output_path)

for def_num in [1,2,3]: 
    exec(f'plt.plot(df_outcomes_college{def_num}[\'College Wage Premium\']'+\
         f', label=\'College Definititon {def_num}\')')
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(color='gainsboro')
plt.suptitle('College Wage Premium', y=0.98, fontsize=14)
plt.title(r'($w^H_C - w^H_N$)', fontsize=10)
plt.legend()
plt.savefig('varyCollegeDef_CollegeWagePremium_RC1.png', dpi=500)
plt.clf()

for def_num in [1,2,3]: 
    exec(f'plt.plot(df_outcomes_college{def_num}[\'Potential Reduction in College Wage Premium\']'+\
         f', label=\'College Definititon {def_num}\')')
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(color='gainsboro')
plt.suptitle('Potential Reduction in College Wage Premium', y=0.98, fontsize=14)
plt.title(r'($w^H_C - w^H_N$) - ($w^P_C - w^P_N$)', fontsize=10)
plt.legend()
plt.savefig('varyCollegeDef_PotentialReduction_RC1.png', dpi=500)
plt.clf()

os.chdir(code_folder)

# How has wedge changed over time:
ref_year = 2019
for def_num in [1,2,3]:
    print(f'College Definition {def_num}:')
    for year in [1997,2000,2007,2010]:
        exec(f'chg_cwp = df_outcomes_college{def_num}.loc[ref_year,\'College Wage Premium\'] -' +\
                    f'df_outcomes_college{def_num}.loc[year,\'College Wage Premium\']')
        exec(f'chg_ESHI_contrib = df_outcomes_college{def_num}.loc[ref_year,\'Potential Reduction in College Wage Premium\'] -' +\
                    f'df_outcomes_college{def_num}.loc[year,\'Potential Reduction in College Wage Premium\']')
        share_ESHI_contrib = chg_ESHI_contrib / chg_cwp
        print(f'Since {year}, '+\
                f'the college wage premium increased by ${chg_cwp:,.0f} from '+\
                f'and ESHI accounts for ${chg_ESHI_contrib:,.0f} of this change or {100*share_ESHI_contrib:,.2f}%.')
    print()
    
#%%  A1. Technical Note: Composition of Some College Around 1992 #%%
#Import Data
os.chdir(data_folder)
df = pd.read_csv('cps_00011.csv')

# Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]
df = df[df['CLASSWLY']!=99]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

# Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

### Define variables for some college and Associates
categories = ['less_than_HS', 'HS', 
              'some_college', 'associates', 'bachelors', 'adv_degree']

df['less_than_HS'] = \
    [int(x in [2, 11, 12, 13, 14, 21, 22, 31, 32, 40, 50, 60, 10,20,30,40,50,60]) for x in df['EDUC']]
df['less_than_HS (weighted)'] = \
    df['less_than_HS'] * df['ASECWT']

df['HS'] = [int(x in [71,72,73]) for x in df['EDUC']]
df['HS (weighted)'] = \
    df['HS'] * df['ASECWT']

df['some_college'] = \
    [int(x in [80,81]) for x in df['EDUC']]
df['some_college (weighted)'] = \
    df['some_college'] * df['ASECWT']

df['associates'] = \
    [int(x in [90,100,91,92]) for x in df['EDUC']]
df['associates (weighted)'] = \
    df['associates'] * df['ASECWT']
    
df['bachelors'] = \
    [int(x in [110,111]) for x in df['EDUC']]
df['bachelors (weighted)'] = \
    df['bachelors'] * df['ASECWT']
    
df['adv_degree'] = \
    [int(x in [121,122,123,124,125]) for x in df['EDUC']]
df['adv_degree (weighted)'] = \
    df['adv_degree'] * df['ASECWT']

# Define working
hours_requirment =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirment =  1*(df['WKSWORK2'] >= 4)
df['working'] = hours_requirment * weeks_requirment
df['working (weighted)'] = hours_requirment * weeks_requirment* df['ASECWT']

# Create this variable to track number of observations after collapse
df['N'] = 1
df['N_working'] = df['working']
for cat in categories:
    df[f'N_{cat}'] = df[f'{cat}']
    df[f'N_{cat}_working'] = df[f'{cat}'] * df['working']

# Create weights 
df['ASECWT']
df['ASECWT_working'] = df['N_working'] * df['ASECWT']
for cat in categories:
    df[f'ASECWT_{cat}'] = df[f'N_{cat}'] * df['ASECWT']
    df[f'ASECWT_{cat}_working'] = df[f'N_{cat}_working'] * df['ASECWT']

# Collapse data by year
data = df.groupby('YEAR').sum()  

# Calculate variables
for cat in categories:
    data[f'share_workers1_{cat}'] = data[f'N_{cat}_working'] / data['N_working']
    data[f'share_workers1_{cat} (weighted)'] = data[f'ASECWT_{cat}_working'] / data['ASECWT_working']
    data[f'share_pop_{cat}'] = data[f'N_{cat}'] / data['N']
    data[f'share_pop_{cat} (weighted)'] = data[f'ASECWT_{cat}'] / data['ASECWT']

#Plot
categories2labels = {'less_than_HS':"Less than HS", 
                     'HS': "High School",
                     'some_college': "Some College", 
                     'associates': "Associate's Degree", 
                     'bachelors': "Bachelor's Degree", 
                     'adv_degree': "Avanced Degree"}

output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/RC1_college'
os.chdir(output_path)
for cat in categories:  
    plt.plot(data[f'share_pop_{cat} (weighted)'], label=categories2labels[cat])
plt.legend()
plt.title("Share of Population", fontsize=14)
plt.savefig('EducationalAttainment.png', dpi=500)
plt.clf()  

os.chdir(code_folder)






