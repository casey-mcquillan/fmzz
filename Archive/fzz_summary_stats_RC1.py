#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 23:29:48 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/SummaryStats"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00011.csv')
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

# Define college attendance
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


# Define Health Insurance
df['HI'] = 1*(df['ANYCOVLY']==2)
df['ESHI'] =   1*(df['GRPCOVLY']==2)
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']

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



#%% Create Table for each Definition #%%

## Choose Relevant year
year = 2019
df = df[df['YEAR']==year]

## Pull Total Population
total_population = OECD_data.loc[year,'Population (25-64)']


### List of Rows and panel titles for LaTeX output
# List of rows
variables = ['Population (millions)', 'Share of Population', 'Share of Workforce',
               'Share of Group', 'Share with ESHI', 'Policyholder', 'Dependent',
               'Share with Other HI', 'Share with No HI', 
               'Employment Rate', 'Avg. Annual Earnings']
# Dictionaries for each group to panel title
group2title_Dict={'Total':'Panel A: Population ages 25-64', 
                  'FTFY':'Panel B: Full-Time, Full-Year Workers ages 25-64', 
                  'PTPY':'Panel C: Part-Time or Part-Year Workers ages 25-64'}
            
            
## Loop through definitions
for def_num in [1,2,3]:
    
    ## Define college variable based on def_num
    df['College'] = df[f'College (Definition {def_num})']
    df['Non-College'] = 1-df['College']


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
            ESHI = np.average(df['ESHI'], weights=df['ASECWT']*group_var*column_var)
            ESHI_own = np.average(df['ESHI_own'], weights=df['ASECWT']*group_var*column_var)
            ESHI_dependent = np.average(df['ESHI_dependent'], weights=df['ASECWT']*group_var*column_var)
            HI_Other = np.average(df['HI Other'], weights=df['ASECWT']*group_var*column_var)
            No_HI = np.average(df['No HI'], weights=df['ASECWT']*group_var*column_var)
            
            ## Labor statistics
            employment_rate = np.average(group_var*column_var, weights=df['ASECWT']*column_var)
            avg_wages = np.average(df['INCWAGE'], weights=df['ASECWT']*group_var*column_var) 
            
            
            ### Append to Dataframe
            table_data.loc[len(table_data)]= group, column, 'Population (millions)', population_level/1000000
            table_data.loc[len(table_data)]= group, column, 'Share of Population', population_share
            table_data.loc[len(table_data)]= group, column, 'Share of Workforce', workforce_share
            table_data.loc[len(table_data)]= group, column, 'Share of Group', group_share
            table_data.loc[len(table_data)]= group, column, 'Share with ESHI', ESHI
            table_data.loc[len(table_data)]= group, column, 'Policyholder', ESHI_own
            table_data.loc[len(table_data)]= group, column, 'Dependent', ESHI_dependent
            table_data.loc[len(table_data)]= group, column, 'Share with Other HI', HI_Other
            table_data.loc[len(table_data)]= group, column, 'Share with No HI', No_HI
            table_data.loc[len(table_data)]= group, column, 'Employment Rate', employment_rate
            table_data.loc[len(table_data)]= group, column, 'Avg. Annual Earnings', avg_wages

            
            ### Inflation Adjust Wages
            '''
            os.chdir(data_folder)
            price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
            adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
            for var in ['wage1_c', 'wage1_n', 'wage1_c (weighted)', 'wage1_n (weighted)']:
                table_data.loc[yearvar] = adj_factor*df.loc[year, var]
            '''    
            
            
        ### Output Latex Table
        
    #Loop through each group
    table_values = []
    for group in ['Total', 'FTFY', 'PTPY']:
        df_panel = table_data[table_data['Group']==group]
            
        # For column in ['Total', 'College', 'Non-college']:
        df_panel_t = df_panel[df_panel['Subgroup']=='Total']
        df_panel_c = df_panel[df_panel['Subgroup']=='College']
        df_panel_n = df_panel[df_panel['Subgroup']=='Non-College']
        
        # Set index to variable
        df_panel_t=df_panel_t.set_index('Variable')
        df_panel_c=df_panel_c.set_index('Variable')
        df_panel_n=df_panel_n.set_index('Variable')
        
        # Remove certain variables for 'Total' Panel
        if group == 'Total':  
            var_list = variables[:-2]
            var_list.remove('Share of Workforce')
            var_list.remove('Share of Group')
        else: var_list = variables
        
        # Loop through each variable
        panel_values = []
        for var in var_list:
            var_t = df_panel_t.loc[var, 'Value']
            var_c = df_panel_c.loc[var, 'Value']
            var_n = df_panel_n.loc[var, 'Value']
            string = f'\t {var} & {var_t:,.3f} & {var_c:,.3f} & {var_n:,.3f} & \\\\ \n'
            
            #Add in break after certain lines
            if group!='Total'and var=='Share with No HI':
                string = string.replace('\\\\', '\medskip \\\\')
            if group=='Total' and var=='Share of Population':
                string = string.replace('\\\\', '\medskip \\\\')
            
            #Adjust Share of Group
            if var=='Share of Group':
                string = f'\t {var} & & {var_c:,.3f} & {var_n:,.3f} & \medskip \\\\ \n'
            
            #Indent 'policyholder' and 'depenndent;
            if var=='Policyholder' or var=='Dependent':
                string = '\t \\ \\ \\ \\ \\small '+ string[2:] 
                
            #Round to nearest dollar for wages
            if var == 'Avg. Annual Earnings':
                string = f'\t {var} & \${var_t:,.0f} & \${var_c:,.0f} & \${var_n:,.0f} & \\\\ \n'
            
           
            
            #Add row to panel values
            panel_values.append(string)
            
        #Concatenate strigns for the panel
        panel_header = ['\multicolumn{5}{l} \n{\\textsl{',
                        group2title_Dict[group],
                        '}} \\\\ \n\hline \n',
                        '& Total & College & Non-College \\\\ \n\hline \n']
        
        panel_bottom = ['\hline \hline \\\\  \n']
        
        #Add panel to table values
        table_values = table_values + panel_header + panel_values + panel_bottom
    
    
    ## Create Table Header and Bottom
    table_header = ['\centering \n',
                    '\\begin{tabular}{lcccccc} \n'
                    '\hline  \n']

    table_bottom = ['\end{tabular}']
            
    #Create, write, and close file
    cwd = os.getcwd()
    os.chdir(output_folder)
    file = open(f"summary_stats_{str(year)}_CollegeDef{def_num}.tex","w")
    file.writelines(table_header) 
    file.writelines(table_values)   
    file.writelines(table_bottom)   
    file.close()