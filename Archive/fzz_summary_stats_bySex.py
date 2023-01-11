#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 15:15:12 2022

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
output_folder = main_folder+"/output/Tables/SummaryStats"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00028.csv')
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
df['College'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']

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


#%% Function to create Summary Stats Table #%%

def gen_summary_stats(sex, data):
    ## Choose Relevant year
    year = 2019
    df_sex = data[data['YEAR']==year]   
    
    # Keep only data for one sex
    if sex=='Male': sex_number=1
    elif sex=='Female': sex_number=2
    
    df_sex = df_sex[df_sex['SEX']==sex_number]
    
    ## Pull Total Population
    total_population = OECD_data.loc[year,'Population (25-64)']
    
    ## Create Dataframe with Table Data
    table_data = pd.DataFrame(columns=['Group', 'Subgroup', 'Variable', 'Value'])
    for group in ['Total', 'FTFY', 'PTPY']:
        group_var = df_sex[group]
        
        for column in ['Total', 'College', 'Non-College']:
            column_var = df_sex[column]
            
            ### Calculations
            ## Shares
            population_share = np.average(group_var*column_var, weights=df_sex['ASECWT'])
            population_level = total_population * population_share
            workforce_share = np.average(group_var*column_var, weights=df_sex['ASECWT']*df_sex['working'])
            group_share = np.average(group_var*column_var, weights=df_sex['ASECWT']*group_var)
            
            ## Health Insurance
            PUB_HI = np.average(df_sex['Public HI'], weights=df_sex['ASECWT']*group_var*column_var)
            PUB_HI_Medicaid = np.average(df_sex['Public HI (Medicaid)'], weights=df_sex['ASECWT']*group_var*column_var)
            PUB_HI_Medicare = np.average(df_sex['Public HI (Medicare)'], weights=df_sex['ASECWT']*group_var*column_var)
            PRVT_HI = np.average(df_sex['Private HI'], weights=df_sex['ASECWT']*group_var*column_var)
            ESHI = np.average(df_sex['ESHI'], weights=df_sex['ASECWT']*group_var*column_var)
            ESHI_own = np.average(df_sex['ESHI_own'], weights=df_sex['ASECWT']*group_var*column_var)
            ESHI_dependent = np.average(df_sex['ESHI_dependent'], weights=df_sex['ASECWT']*group_var*column_var)
            Other_PRVT_HI = np.average(df_sex['Other Private'], weights=df_sex['ASECWT']*group_var*column_var)
            HI_Other = np.average(df_sex['HI Other'], weights=df_sex['ASECWT']*group_var*column_var)
            No_HI = np.average(df_sex['No HI'], weights=df_sex['ASECWT']*group_var*column_var)
            
            ## Offer, Eligibility, and Take-up
            ESHI_offered = np.average(df_sex['ESHI_offered'], 
                                      weights=df_sex['ASECWT']*group_var*column_var)
            ESHI_offered_takeup = np.average(df_sex['ESHI_own'], 
                                             weights=df_sex['ASECWT']*group_var*column_var*df_sex['ESHI_offered'])
            ESHI_eligible = np.average(df_sex['ESHI_eligible'], 
                                       weights=df_sex['ASECWT']*group_var*column_var)
            ESHI_eligible_takeup = np.average(df_sex['ESHI_own'], 
                                              weights=df_sex['ASECWT']*group_var*column_var*df_sex['ESHI_eligible'])
            
            ### Labor statistics
            employment_rate = np.average(group_var*column_var, weights=df_sex['ASECWT']*column_var)
            avg_wages = np.average(df_sex['INCWAGE'], weights=df_sex['ASECWT']*group_var*column_var) 
            
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


    ### Output Latex Table #%%
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
                   #'ESHI Eligible',
                   #'Take-up | ESHI Eligible']
    
    #Dictionaries for each group to panel vairables
    panel2panelVariables_Dict={'A':variables_A, 
                      'B':variables_B,
                      'C':variables_C}
    
    #Dictionaries for each group to panel title
    panel2title_Dict={'A':f'Panel A: Labor Market Outcomes ({sex})', 
                      'B':f'Panel B: Health Insurance Coverage ({sex})',
                      'C':f'Panel C: Offering and Take-up ({sex})'}
    
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
        panel_variables_list = panel2panelVariables_Dict[panel]
        # Loop through each variable
        panel_values = []
        for var in panel_variables_list:
            var_t = df_panel_t.loc[var, 'Value']
            var_c = df_panel_c.loc[var, 'Value']
            var_n = df_panel_n.loc[var, 'Value']
            string = f'\t {var} & {var_t:,.3f} & {var_c:,.3f} & {var_n:,.3f} & \\\\ \n'
                
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
    file = open(f"summary_stats_{str(year)}_{sex}.tex","w")
    file.writelines(table_header) 
    file.writelines(table_values)   
    file.writelines(table_bottom)   
    file.close()
    
    
#%% Execution #%%
gen_summary_stats('Male', df)
gen_summary_stats('Female', df)
    
    