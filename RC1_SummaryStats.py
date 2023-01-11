#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 22:47:06 2022
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
from main import main_folder
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder = main_folder+"/output/Tables/"


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00012.csv')
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')

#%% Data Cleaning #%%

# Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE', 'ANYCOVLY', 'GRPCOVLY']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

# Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

##############################################################################
# Define college attendance as Some College or More
df['College'] = \
    [int(x in [80, 90, 100, 110, 120, 121, 122, 81, 91, 92, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']
###############################################################################

# Define Health Insurance
df['HI'] = 1*(df['ANYCOVLY']==2)
df['Public HI'] =   1*(df['PUBCOVLY']==2)
df['Public HI (Medicaid)'] =   1*(df['HIMCAIDLY']==2)
df['Public HI (Medicare)'] =   1*(df['HIMCARELY']==2)
df['Private HI'] =   1*(df['PRVTCOVLY']==2)
df['ESHI'] =   1*(df['GRPCOVLY']==2)
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['Other Private'] = df['Private HI'] - df['ESHI']
df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']

# Offering and Eligibility
df['ESHI_offered'] = 1*(df['HIOFFER']==2) + \
    1*((1-1*(df['HIOFFER']==2))*(1*df['GRPOWNLY']==2))
df['ESHI_eligible'] = 1*(df['HIELIG']==2) + \
    1*((1-1*(df['HIELIG']==2))*(1*df['GRPOWNLY']==2))

## Define Full-Time, Full-Year
hours_requirement_FTFY =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement_FTFY =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement_FTFY * weeks_requirement_FTFY
df_FTFY = df[df['FTFY']==1]

## Define Part-Time, Part-Year
hours_requirement_PTPY =  1*(df['UHRSWORKLY'] > 0)
weeks_requirement_PTPY =  1*(df['WKSWORK2'] > 0)
df['PTPY'] = hours_requirement_PTPY * weeks_requirement_PTPY
df['PTPY'] = df['PTPY']-df['FTFY']
df_PTPY = df[df['PTPY']==1]

#Define Workforce (FTFY or PTPY)
df['working'] =  df['PTPY']+df['FTFY']

# Constant column
df['Total'] = 1


#%% Create Table Data #%%

## Choose Relevant year
year = 2019
df = df[df['YEAR']==year]   
        
## Pull Total Population
total_population = OECD_data.loc[year,'Population (25-64)']

## Create Dataframe with Table Data
table_data = pd.DataFrame(columns=['Group', 'Subgroup', 'Variable', 'Value'])
for group in ['Total', 'FTFY', 'PTPY']:
    group_var = df[group]
    
    for column in ['Total', 'College', 'Non-College']:
        column_var = df[column]
        
        ### Calculations
        ## Shares
        population_share = np.average(group_var*column_var, weights=df['ASECWT'])
        population_level = total_population * population_share
        workforce_share = np.average(group_var*column_var, weights=df['ASECWT']*df['working'])
        group_share = np.average(group_var*column_var, weights=df['ASECWT']*group_var)
        
        ## Health Insurance
        PUB_HI = np.average(df['Public HI'], weights=df['ASECWT']*group_var*column_var)
        PUB_HI_Medicaid = np.average(df['Public HI (Medicaid)'], weights=df['ASECWT']*group_var*column_var)
        PUB_HI_Medicare = np.average(df['Public HI (Medicare)'], weights=df['ASECWT']*group_var*column_var)
        PRVT_HI = np.average(df['Private HI'], weights=df['ASECWT']*group_var*column_var)
        ESHI = np.average(df['ESHI'], weights=df['ASECWT']*group_var*column_var)
        ESHI_own = np.average(df['ESHI_own'], weights=df['ASECWT']*group_var*column_var)
        ESHI_dependent = np.average(df['ESHI_dependent'], weights=df['ASECWT']*group_var*column_var)
        Other_PRVT_HI = np.average(df['Other Private'], weights=df['ASECWT']*group_var*column_var)
        HI_Other = np.average(df['HI Other'], weights=df['ASECWT']*group_var*column_var)
        No_HI = np.average(df['No HI'], weights=df['ASECWT']*group_var*column_var)
        
        ## Offer, Eligibility, and Take-up
        ESHI_offered = np.average(df['ESHI_offered'], 
                                  weights=df['ASECWT']*group_var*column_var)
        ESHI_offered_takeup = np.average(df['ESHI_own'], 
                                         weights=df['ASECWT']*group_var*column_var*df['ESHI_offered'])
        ESHI_eligible = np.average(df['ESHI_eligible'], 
                                   weights=df['ASECWT']*group_var*column_var)
        ESHI_eligible_takeup = np.average(df['ESHI_own'], 
                                          weights=df['ASECWT']*group_var*column_var*df['ESHI_eligible'])
        
        ### Labor statistics
        employment_rate = np.average(group_var*column_var, weights=df['ASECWT']*column_var)
        avg_wages = np.average(df['INCWAGE'], weights=df['ASECWT']*group_var*column_var) 
        
        ### Append to Dataframe
        ### Define rows of table:
        table_data.loc[len(table_data)]= group, column, 'Population (millions)', population_level/1000000
        table_data.loc[len(table_data)]= group, column, 'Share of Population', population_share
        table_data.loc[len(table_data)]= group, column, 'Share of Workforce', workforce_share
        table_data.loc[len(table_data)]= group, column, 'Share of Group', group_share
        
        table_data.loc[len(table_data)]= group, column, 'Share with Public HI', PUB_HI
        table_data.loc[len(table_data)]= group, column, 'Share with Public HI (Medicaid)', PUB_HI_Medicaid
        table_data.loc[len(table_data)]= group, column, 'Share with Public HI (Medicare)', PUB_HI_Medicare
        table_data.loc[len(table_data)]= group, column, 'Share with Private HI', PRVT_HI
        table_data.loc[len(table_data)]= group, column, 'Employer-Sponsored', ESHI
        table_data.loc[len(table_data)]= group, column, 'Policyholder', ESHI_own
        table_data.loc[len(table_data)]= group, column, 'Dependent', ESHI_dependent
        table_data.loc[len(table_data)]= group, column, 'Share with Other HI', HI_Other
        table_data.loc[len(table_data)]= group, column, 'Other Private', Other_PRVT_HI
        table_data.loc[len(table_data)]= group, column, 'Public', PUB_HI
        table_data.loc[len(table_data)]= group, column, 'None', No_HI
        
        table_data.loc[len(table_data)]= group, column, 'Offered Employer-Sponsored Health Insurance', ESHI_offered
        table_data.loc[len(table_data)]= group, column, 'Take-up | ESHI Offered', ESHI_offered_takeup
        table_data.loc[len(table_data)]= group, column, 'ESHI Eligible', ESHI_eligible
        table_data.loc[len(table_data)]= group, column, 'Take-up | ESHI Eligible', ESHI_eligible_takeup
        
        table_data.loc[len(table_data)]= group, column, 'Employment Rate', employment_rate
        table_data.loc[len(table_data)]= group, column, 'Avg. Annual Earnings', avg_wages
    
        
#%% Output Latex Table #%%

#List of variables by Panel
variables_A = ['Employment Rate', 
               'Avg. Annual Earnings']
variables_B = ['Employer-Sponsored',
               'Policyholder', 
               'Dependent',
               'Other Private', 
               'Public',
               'None']
variables_C = ['Offered Employer-Sponsored Health Insurance',
               'Take-up | ESHI Offered']

#Dictionaries for each group to panel title
panel2title_Dict={'A':'Panel A: Labor Market Outcomes', 
                  'B':'Panel B: Health Insurance Coverage',
                  'C':'Panel C: Offering and Take-up'}

# Subset to FTFY Workers
df_panel = table_data[table_data['Group']=='FTFY']
        
# Subset for columns in ['Total', 'College', 'Non-college']:
df_panel_t = df_panel[df_panel['Subgroup']=='Total']
df_panel_c = df_panel[df_panel['Subgroup']=='College']
df_panel_n = df_panel[df_panel['Subgroup']=='Non-College']

# Set index to variable
df_panel_t=df_panel_t.set_index('Variable')
df_panel_c=df_panel_c.set_index('Variable')
df_panel_n=df_panel_n.set_index('Variable')

# Loop through each panel
table_values = []
for panel in ['A', 'B', 'C']:
    panel_variables_list = []
    exec(f'panel_variables_list = variables_{panel}')
    # Loop through each variable
    panel_values = []
    for var in panel_variables_list:
        var_t = df_panel_t.loc[var, 'Value']
        var_c = df_panel_c.loc[var, 'Value']
        var_n = df_panel_n.loc[var, 'Value']
        string = f'\t {var} & {var_t:,.3f} & {var_c:,.3f} & {var_n:,.3f} & \\\\ \n'
        
        '''
        #Add in break after certain lines
        if group!='Total'and var=='Share with No HI':
            string = string.replace('\\\\', '\medskip \\\\')
        if group=='Total' and var=='Share of Population':
            string = string.replace('\\\\', '\medskip \\\\')
        '''
            
        #Add LaTeX code for employment rate: 
        if var == 'Employment Rate':
            string = f'\t {var} ($P_g$) & {var_t:,.3f} & {var_c:,.3f} & {var_n:,.3f} & \\\\ \n'
            
        #Round to nearest dollar and add LaTeX code for wages:
        if var == 'Avg. Annual Earnings':
            string = f'\t {var} ($w_g$) & \${var_t:,.0f} & \${var_c:,.0f} & \${var_n:,.0f} & \\\\ \n'
        
        #Indent subcategories;
        if var in ['Policyholder', 'Dependent', 'Take-up | ESHI Offered', 'Take-up | ESHI Eligible']:
            string = '\t \\ \\ \\ \\ \\small '+ string[2:] 
        
        #Vertical bar is math symbol
        if var in ['Take-up | ESHI Offered', 'Take-up | ESHI Eligible']:
            string=string.replace('|','$|$')
            
        if var == 'Take-up | ESHI Offered':
            string=string.replace(' & \\\\ \n',' & \\medskip \\\\ \n')
        
        #Add row to panel values
        panel_values.append(string)
    
    #Concatenate strigns for the panel
    panel_header = ['\multicolumn{5}{l} \n{\\textsl{',
                    panel2title_Dict[panel],
                    '}} \\\\ \n\hline \n']
    if panel=='A':
        panel_header = panel_header \
                        + ['& Total & College & Non-College \\\\ \n\hline \n']
    
    panel_bottom = ['\\\\  \n']
    if panel=='C':
        panel_bottom = ['\hline \hline \\\\  \n']

    #Add panel to table values
    table_values = table_values + panel_header + panel_values + panel_bottom
    
## Create Table Header and Bottom
table_header = ['\centering \n',
                '\\begin{tabular}{lcccccc} \n']

table_bottom = ['\end{tabular}']
        
#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"RC1_summary_stats_{str(year)}.tex","w")
file.writelines(table_header) 
file.writelines(table_values)   
file.writelines(table_bottom)   
file.close()
