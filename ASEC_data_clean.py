#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 16:47:40 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)


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

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

#Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

# Define college attendance
df['college'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]

# Define working
hours_requirement =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement =  1*(df['WKSWORK2'] >= 4)
worker_class_requirement = [int(not x in [10,13,14,29]) for x in df['CLASSWLY']]

df['working'] = hours_requirement * weeks_requirement * worker_class_requirement
df['working (weighted)'] = hours_requirement * weeks_requirement * worker_class_requirement * df['ASECWT']

# Collect wage data
df['wage_college'] = df['working'] * df['college'] * df['INCWAGE']
df['wage_noncollege'] = df['working'] * (1 - df['college']) * df['INCWAGE']

df['wage_college (weighted)'] = df['working'] * df['college'] * df['INCWAGE'] * df['ASECWT'] 
df['wage_noncollege (weighted)'] = df['working'] * (1 - df['college']) * df['INCWAGE'] * df['ASECWT']


#%% Data Collapse #%%
# Create this variable to track number of observations after collapse
df['N'] = 1
df['N_college'] = df['college']
df['N_noncollege'] = 1 - df['college']
df['N_working'] = df['working']
df['N_college_working'] = df['college'] * df['working']
df['N_noncollege_working'] = (1-df['college']) * df['working']

# Create weights 
df['ASECWT']
df['ASECWT_college'] = df['N_college'] * df['ASECWT']
df['ASECWT_noncollege'] = df['N_noncollege'] * df['ASECWT']
df['ASECWT_working'] = df['N_working'] * df['ASECWT']
df['ASECWT_college_working'] = df['N_college_working'] * df['ASECWT']
df['ASECWT_noncollege_working'] = df['N_noncollege_working'] * df['ASECWT']

# Collapse data by year
data = df.groupby('YEAR').sum()  

# Calculate variables
data['P1_c'] = data['N_college_working'] / data['N_college']
data['P1_c (weighted)'] = data['ASECWT_college_working'] / data['ASECWT_college']

data['P1_n'] = data['N_noncollege_working'] / data['N_noncollege']
data['P1_n (weighted)'] = data['ASECWT_noncollege_working'] / data['ASECWT_noncollege']

data['share_workers1_c'] = data['N_college_working'] / data['N_working']
data['share_workers1_c (weighted)'] = data['ASECWT_college_working'] / data['ASECWT_working']

data['share_pop_c'] = data['N_college'] / data['N']
data['share_pop_c (weighted)'] = data['ASECWT_college'] / data['ASECWT']

#Calculate wages
data['wage1_c'] = \
    data['wage_college'] / data['N_college_working'] 
data['wage1_n'] = \
    data['wage_noncollege'] / data['N_noncollege_working']

data['wage1_c (weighted)'] = \
    data['wage_college (weighted)'] / data['ASECWT_college_working']
data['wage1_n (weighted)'] = \
    data['wage_noncollege (weighted)'] / data['ASECWT_noncollege_working']
    
    
#%% Inflation Adjust #%%
# Adjust wages to be in 2019 dollars
os.chdir(data_folder)
price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
for year in data.index:
    adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
    for var in ['wage1_c', 'wage1_n', 'wage1_c (weighted)', 'wage1_n (weighted)']:
        data.loc[year, var] = adj_factor*data.loc[year, var]
        

#%% Export Data #%%
os.chdir(data_folder)
data_export = data[['N', 'N_college', 'N_working', 'N_college_working',
                    'share_pop_c', 'share_pop_c (weighted)', 
                    'share_workers1_c', 'share_workers1_c (weighted)',
                    'P1_c', 'P1_c (weighted)',
                    'P1_n', 'P1_n (weighted)',
                    'wage1_c', 'wage1_c (weighted)',
                    'wage1_n', 'wage1_n (weighted)']]
data_export.to_csv('CPS_ASEC_clean.csv')    