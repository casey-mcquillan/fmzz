#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 23:00:25 2023
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import appendix_output_folder


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('raw_ASEC_data.csv')
OECD_data = pd.read_csv('clean_OECD_data.csv', index_col='year')


#%% Data Cleaning #%%

# Drop invalid responses
#for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE', 'ANYCOVLY', 'GRPCOVLY']:
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE', 'SEX']:
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
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['ESHI'] = 1*(df['GRPOWNLY']==2) + (1-(df['GRPOWNLY']==2))*(df['GRPDEPLY']==2)
df['Other Private'] = 1*(df['PRVTCOVLY']==2) - df['ESHI']
df['Public HI'] =   1*(df['PUBCOVLY']==2)
df['No HI'] = 1 - 1*(df['ANYCOVLY']==2)

# Offering and Eligibility
df['ESHI_offered'] = 1*(df['HIOFFER']==2) + \
    1*((1-1*(df['HIOFFER']==2))*(1*df['GRPOWNLY']==2))
df['ESHI_eligible'] = 1*(df['HIELIG']==2) + \
    1*((1-1*(df['HIELIG']==2))*(1*df['GRPOWNLY']==2))

## Define Full-Time, Full-Year
hours_requirement_FTFY =  1*(df['UHRSWORKLY'] >= 30)
weeks_requirement_FTFY =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement_FTFY * weeks_requirement_FTFY
df_FTFY = df[df['FTFY']==1]

## Define Part-Time, Part-Year
hours_requirement_PTPY =  1*(df['UHRSWORKLY'] > 0)
weeks_requirement_PTPY =  1*(df['WKSWORK2'] > 0)
df['PTPY'] = hours_requirement_PTPY * weeks_requirement_PTPY
df['PTPY'] = df['PTPY']-df['FTFY']
df_PTPY = df[df['PTPY']==1]

## Define Sex
df['Male'] = 1*(df['SEX']==1)
df['Female'] = 1*(df['SEX']==2)

# Constant column
df['Total'] = 1

#%% Create Table Data #%%
## Create Dataframe with Table Data
data = pd.DataFrame(columns=['Year', 'Group', 'Subgroup', 'Sex', 'Variable', 'Value',])

## Choose Relevant year
for year in range(1995,2020):
    year_var = 1*(df['YEAR']==year)   
                
    #for group in ['Total', 'FTFY', 'PTPY']:
    group = 'FTFY'
    group_var = df[group]
    
    for column in ['Total', 'College', 'Non-College']:
        column_var = df[column]
        
        for sex in ['Total', 'Female', 'Male']:
            sex_var = df[sex]
                
            ### Calculations        
            ## Health Insurance
            ESHI = np.average(df['ESHI'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            ESHI_own = np.average(df['ESHI_own'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            ESHI_dependent = np.average(df['ESHI_dependent'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            # Other_PRVT_HI = np.average(df['Other Private'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            # PUB_HI = np.average(df['Public HI'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            # No_HI = np.average(df['No HI'], weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            
            # ## Offer, Eligibility, and Take-up
            # ESHI_offered = np.average(df['ESHI_offered'], 
            #                           weights=df['ASECWT']*year_var*group_var*column_var*sex_var)
            # ESHI_offered_takeup = np.average(df['ESHI_own'], 
            #                                  weights=df['ASECWT']*year_var*group_var*column_var*sex_var*df['ESHI_offered'])
            # ESHI_eligible = np.average(df['ESHI_eligible'], 
            #                            weights=df['ASECWT']*group_var*column_var)
            # ESHI_eligible_takeup = np.average(df['ESHI_own'], 
            #                                   weights=df['ASECWT']*year_var*group_var*column_var*sex_var*df['ESHI_eligible'])
            
            
            ### Append to Dataframe
            ### Define rows of table:        
            data.loc[len(data)]= year, group, column, sex, 'Employer-Sponsored', ESHI
            data.loc[len(data)]= year, group, column, sex, 'Employer-Sponsored (Policyholder)', ESHI_own
            data.loc[len(data)]= year, group, column, sex, 'Employer-Sponsored (Dependent)', ESHI_dependent
            # data.loc[len(data)]= year, group, column, 'Other Private', Other_PRVT_HI
            # data.loc[len(data)]= year, group, column, 'Public', PUB_HI
            # data.loc[len(data)]= year, group, column, 'None', No_HI
            
            # data.loc[len(data)]= year, group, column, 'Offered Employer-Sponsored Health Insurance', ESHI_offered
            # data.loc[len(data)]= year, group, column, 'Take-up | Offered', ESHI_offered_takeup
            # data.loc[len(data)]= year, group, column, 'ESHI Eligible', ESHI_eligible
            # data.loc[len(data)]= year, group, column, 'Take-up | Eligible', ESHI_eligible_takeup


#%% Output Figures #%%


# Import necessary Packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False


# Define variables, groups, sexes
variables = ['Employer-Sponsored',
               'Employer-Sponsored (Policyholder)', 
               'Employer-Sponsored (Dependent)']
education_groups = ['College', 'Non-College']
sexes = ['Female', "Male"]
years = range(1995,2020)



# Loop through variables without changing sex
graph_data = data[data['Sex']=='Total']
for var in variables:
    # Only data for that value
    plot_lines = graph_data[graph_data['Variable']==var]
    
    #Loop through subgroup to plot
    for educ in education_groups:
        
        # Only data for that subgroup
        plot_line = plot_lines[plot_lines['Subgroup']==educ]
        # Set index to year
        plot_line=plot_line.set_index('Year')

        #Determine line color
        if educ=='College': line_color='firebrick'
        if educ=='Non-College': line_color='royalblue'
        
        #Plot line for this variable x subgroup
        plt.plot(plot_line['Value'], label=educ, 
                 color=line_color, marker='.')
    
    # Save plot for this variable
    plt.legend()
    plt.title(var, fontsize=14)
    plt.grid(axis='y', color='gainsboro')
    os.chdir(appendix_output_folder)
    plt.savefig(var+'.png', dpi=500)
    plt.clf() 
    
    
# Loop through variables by sex
graph_data = data[data['Sex']!='Total']
for var in variables:
    # Only data for that value
    plot_lines = graph_data[graph_data['Variable']==var]
    
    #Loop through subgroup to plot
    for educ in education_groups:
        
        # Only data for that subgroup
        plot_line = plot_lines[plot_lines['Subgroup']==educ]

        #Break by gender
        plot_line_f=plot_line[plot_line['Sex']=='Female']
        plot_line_m=plot_line[plot_line['Sex']=='Male']
        
        # Set index to year
        plot_line_f=plot_line_f.set_index('Year')
        plot_line_m=plot_line_m.set_index('Year')

        #Determine line color
        if educ=='College': line_color='firebrick'
        if educ=='Non-College': line_color='royalblue'
        
        #Plot line for this variable x subgroup
        plt.plot(plot_line_f['Value'], label=educ+", Female", 
                 linestyle='dotted', color=line_color, marker='.')
        plt.plot(plot_line_m['Value'], label=educ+", Male", 
                 linestyle='dashed', color=line_color, marker='.')
    
    # Save plot for this variable
    plt.legend()
    plt.title(var, fontsize=14)
    plt.grid(axis='y', color='gainsboro')
    os.chdir(appendix_output_folder)
    plt.savefig(var+' by Sex.png', dpi=500)
    plt.clf() 
    

#%% Return to code directory #%%
os.chdir(code_folder)