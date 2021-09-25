#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 21:05:19 2021

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


#%% Data Cleaning #%%
os.chdir(data_folder)

# Read in data
df = pd.read_csv('CPS_ASEC_data.csv')

# Subset data to the year and education variables
df = df[['YEAR', 'EDUC', 'ASECWT']]

# Create this variable to track number of observations after collapse
df['N'] = 1

# Drop non-responses
df = df[[not np.isnan(x) for x in df['EDUC']]]
df = df[df['EDUC'] != 999]

#Create variable for college educated
df['Bachelor\'s Degree or More'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]

df['Bachelor\'s Degree or More (Weighted)'] = \
    df['Bachelor\'s Degree or More'] * df['ASECWT']

#Collapse data by year
df = df.groupby('YEAR').sum()

#Calculate share educated
df['Bachelor\'s Degree or More'] = \
    df['Bachelor\'s Degree or More'] / df['N']
df['Bachelor\'s Degree or More (Weighted)'] = \
    df['Bachelor\'s Degree or More (Weighted)'] / df['ASECWT']


#%%  Data Export #%%
## Select relevant variables
data_export = df['Bachelor\'s Degree or More (Weighted)']
data_export = data_export.rename("share_pop_c")

## Export data
os.chdir(data_folder)
data_export.to_csv('share_pop_c_ASEC.csv')