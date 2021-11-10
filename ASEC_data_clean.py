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
df['YEAR'] = df['YEAR'] - 1

#%% Create Share of Population with College Education #%%
df1 = df

#Drop invalid responses
df1 = df1[[not np.isnan(x) for x in df1['EDUC']]]
df1 = df1[[not x in [0,1,999] for x in df1['EDUC']]]

# Create this variable to track number of observations after collapse
df1['N'] = 1

# Define college attendance
df1['college'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df1['EDUC']]
df1['college (weighted)'] = \
    df1['college'] * df1['ASECWT']

#Create collapsed data frame
data = df1.groupby('YEAR').sum()  
   
#Calculate share educated 
data['share_pop_c'] = \
    data['college'] / data['N']
data['share_pop_c (weighted)'] = \
    data['college (weighted)'] / data['ASECWT']

## Store data
share_pop_c = data[['share_pop_c', 'share_pop_c (weighted)']]


#%% Create Export for Share of Workforce with College Education #%%
df2 = df

# Drop nan observations
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df2 = df2[[not np.isnan(x) for x in df2[var]]]
    
# Drop other invalid responses
df2 = df2[[not x in [0,1,999] for x in df2['EDUC']]]
df2 = df2[[not x in [0,9] for x in df2['WKSWORK2']]]
df2 = df2[df2['UHRSWORKLY']!=999]
df2 = df2[df2['CLASSWLY']!=99]

# Drop those who didn't work full-time, full-year
df2 = df2[df2['UHRSWORKLY'] >= 35]
df2 = df2[df2['WKSWORK2'] >= 4]
df2 = df2[[not x in [13,14,29] for x in df2['CLASSWLY']]]

# Define college attendance
df2['college'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df2['EDUC']]
df2['college (weighted)'] = \
    df2['college'] * df2['ASECWT']
    
# Create this variable to track number of observations after collapse
df2['N'] = 1

# Create these variables to track average wages after collapse
df2['wage_college'] = df2['college'] * df2['INCWAGE']
df2['wage_noncollege'] = (1 - df2['college']) * df2['INCWAGE']

df2['wage_college (weighted)'] = df2['college'] * df2['INCWAGE'] * df2['ASECWT'] 
df2['wage_noncollege (weighted)'] = (1 - df2['college']) * df2['INCWAGE'] * df2['ASECWT']
df2['ASECWT_college'] = df2['college'] * df2['ASECWT']
df2['ASECWT_noncollege'] = (1 - df2['college']) * df2['ASECWT']

#Create collapsed data frame
data = df2.groupby('YEAR').sum()  
   
#Calculate share educated 
data['share_workers1_c'] = \
    data['college'] / data['N']
data['share_workers1_c (weighted)'] = \
    data['college (weighted)'] / data['ASECWT']
    
#Calculate wages
data['wage1_c'] = \
    data['wage_college'] / data['college'] 
data['wage1_n'] = \
    data['wage_noncollege'] / (data['N'] - data['college'])
data['wage1_c (weighted)'] = \
    data['wage_college (weighted)'] / data['ASECWT_college']
data['wage1_n (weighted)'] = \
    data['wage_noncollege (weighted)'] / data['ASECWT_noncollege']

# Adjust wages to be in 2019 dollars
os.chdir(data_folder)
price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
for year in data.index:
    adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
    for var in ['wage1_c', 'wage1_n', 'wage1_c (weighted)', 'wage1_n (weighted)']:
        data.loc[year, var] = adj_factor*data.loc[year, var]
        
## Store data
share_workers1_c = data[['share_workers1_c', 'share_workers1_c (weighted)']]
wage = data[['wage1_c', 'wage1_n', 'wage1_c (weighted)', 'wage1_n (weighted)']]


#%% Calculate share of each group that chooses to work #%%
df3 = df

#Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df3 = df3[[not np.isnan(x) for x in df3[var]]]
df3 = df3[[not x in [0,1,999] for x in df3['EDUC']]]
df3 = df3[df3['WKSWORK2']!=9]
df3 = df3[df3['CLASSWLY']!=99]

# Define college attendance
df3['college'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df3['EDUC']]
df3['college (weighted)'] = \
    df3['college'] * df3['ASECWT']

# Define working
hours_requirment =  1*(df3['UHRSWORKLY'] >= 35)
weeks_requirment =  1*(df3['WKSWORK2'] >= 4)
worker_class_requirement = [int(not x in [13,14,29]) for x in df3['CLASSWLY']]

df3['working'] = hours_requirment * weeks_requirment * worker_class_requirement
df3['working (weighted)'] = hours_requirment * weeks_requirment* df3['ASECWT']

# Create this variable to track number of observations after collapse
df3['N'] = 1

# Separate based on education
df3_c = df3[df3['college'] == 1]
df3_n = df3[df3['college'] == 0]

#Create collapsed data frame
data_c = df3_c.groupby('YEAR').sum()
data_n = df3_n.groupby('YEAR').sum()
   
#Calculate share educated 
data_c['P1_c'] = \
    data_c['working'] / data_c['N']
data_c['P1_c (weighted)'] = \
    data_c['working (weighted)'] / data_c['ASECWT']
    
data_n['P1_n'] = \
    data_n['working'] / data_n['N']
data_n['P1_n (weighted)'] = \
    data_n['working (weighted)'] / data_n['ASECWT']

## Store data
LFP_shares = pd.concat([data_c[['P1_c', 'P1_c (weighted)']], data_n[['P1_n','P1_n (weighted)']]], axis=1)


#%% Export Data #%%
os.chdir(data_folder)
data_export = pd.concat([share_pop_c, share_workers1_c, wage,LFP_shares], axis=1)
data_export.to_csv('CPS_ASEC_clean.csv')
