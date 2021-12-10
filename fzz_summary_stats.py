#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 10:35:11 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np
import math

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_path = "/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/SummaryStats"
os.chdir(code_folder)


#%% Functions #%%
def weighted_avg_and_std(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00009.csv')


#%% Data Wrangling #%%
#Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]
df = df[df['CLASSWLY']!=99]

#Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

# Define college attendance
df['college'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]

# Define working
hours_requirment =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirment =  1*(df['WKSWORK2'] >= 4)
worker_class_requirement = [int(not x in [13,14,29]) for x in df['CLASSWLY']]

df['working'] = hours_requirment * weeks_requirment * worker_class_requirement

# Collect wage data conditional on working
df['wage'] = df['working'] * df['INCWAGE']
df['wage_college'] = df['working'] * df['college'] * df['INCWAGE']
df['wage_noncollege'] = df['working'] * (1 - df['college']) * df['INCWAGE']

df['log_wage'] = df['working'] * np.log(df['INCWAGE']+1)
df['log_wage_college'] = df['working'] * df['college'] * np.log(df['INCWAGE']+1)
df['log_wage_noncollege'] = df['working'] * (1 - df['college']) * np.log(df['INCWAGE']+1)


#%% Data Collapse #%%
# Create this variable to track number of observations after collapse
df['N'] = 1
df['noncollege'] = 1 - df['college']
df['college_working'] = df['college'] * df['working']
df['noncollege_working'] = (1-df['college']) * df['working']

# Create weights 
df['ASECWT']
df['ASECWT_college'] = df['college'] * df['ASECWT']
df['ASECWT_noncollege'] = df['noncollege'] * df['ASECWT']
df['ASECWT_working'] = df['working'] * df['ASECWT']
df['ASECWT_college_working'] = df['college_working'] * df['ASECWT']
df['ASECWT_noncollege_working'] = df['noncollege_working'] * df['ASECWT']



#Defines variables and outcomes of interest
variables = ['Share of Population with a College Degree', 'Share of Workforce with a College Degree',
             'Share of Population without a College Degree', 'Share of Workforce without a College Degree',
             'Wages', 'Wages (College)', 'Wages (Non-college)', 
             'Log Wages', 'Log Wages (College)', 'Log Wages (Non-college)',
             'Employment Rate', 'Employment Rate (College)', 'Employment Rate (Non-college)', 
             'Labor Supply', 'Labor Supply (College)', 'Labor Supply (Non-college)']

outcomes = ["Average", "Standard Deviation"]

summary_stats = pd.DataFrame(index=outcomes, columns=variables)

# Calculate based on data
# Select Year
df_ss = df[df['YEAR']==2019]

# Population Share
summary_stats.loc[outcomes,'Share of Population with a College Degree'] \
    = weighted_avg_and_std(values=df_ss['college'], weights=df_ss['ASECWT'])
summary_stats.loc[outcomes,'Share of Population without a College Degree'] \
    = weighted_avg_and_std(values=df_ss['noncollege'], weights=df_ss['ASECWT'])

# Workforce Share
summary_stats.loc[outcomes,'Share of Workforce with a College Degree'] \
    = weighted_avg_and_std(values=df_ss['college'], weights=df_ss['ASECWT_working'])
summary_stats.loc[outcomes,'Share of Workforce without a College Degree'] \
    = weighted_avg_and_std(values=df_ss['noncollege'], weights=df_ss['ASECWT_working'])

# Wages
summary_stats.loc[outcomes, 'Wages'] \
    = weighted_avg_and_std(values=df_ss['wage'], weights=df_ss['ASECWT_working'])
summary_stats.loc[outcomes, 'Wages (College)'] \
    = weighted_avg_and_std(values=df_ss['wage_college'], weights=df_ss['ASECWT_college_working'])
summary_stats.loc[outcomes, 'Wages (Non-college)'] \
    = weighted_avg_and_std(values=df_ss['wage_noncollege'], weights=df_ss['ASECWT_noncollege_working'])

# Log Wages
summary_stats.loc[outcomes,'Log Wages'] \
    = weighted_avg_and_std(values=df_ss['log_wage'], weights=df_ss['ASECWT_working'])
summary_stats.loc[outcomes,'Log Wages (College)'] \
    = weighted_avg_and_std(values=df_ss['log_wage_college'], weights=df_ss['ASECWT_college_working'])
summary_stats.loc[outcomes,'Log Wages (Non-college)'] \
    = weighted_avg_and_std(values=df_ss['log_wage_noncollege'], weights=df_ss['ASECWT_noncollege_working'])

# Employment Rates
summary_stats.loc[outcomes,'Employment Rate'] \
    =weighted_avg_and_std(values=df_ss['working'], weights=df_ss['ASECWT'])
summary_stats.loc[outcomes,'Employment Rate (College)'] \
    =weighted_avg_and_std(values=df_ss['working'], weights=df_ss['ASECWT_college'])
summary_stats.loc[outcomes,'Employment Rate (Non-college)'] \
    =weighted_avg_and_std(values=df_ss['working'], weights=df_ss['ASECWT_noncollege'])

#Labor Supply
summary_stats.loc[outcomes,'Labor Supply'] \
    =weighted_avg_and_std(values=df_ss['working'], weights=df_ss['ASECWT'])
summary_stats.loc[outcomes,'Labor Supply (College)'] \
    =weighted_avg_and_std(values=df_ss['college_working'], weights=df_ss['ASECWT'])
summary_stats.loc[outcomes,'Labor Supply (Non-college)'] \
    =weighted_avg_and_std(values=(df_ss['noncollege_working']), weights=df_ss['ASECWT'])


#%% Inflation Adjust #%%
'''
# Adjust wages to be in 2019 dollars
os.chdir(data_folder)
price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
for year in data.index:
    adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
    for var in ['wage1_c', 'wage1_n', 'wage1_c (weighted)', 'wage1_n (weighted)']:
        data.loc[year, var] = adj_factor*data.loc[year, var]
'''

#%% Export Data #%%
summary_stats.T.to_excel(output_path+'/SummaryStats2019.xlsx', index = True)