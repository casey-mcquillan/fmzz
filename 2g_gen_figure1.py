#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 18:03:30 2023

@author: caseymcquillan
"""
#%%     Preamble        #%%  
### Import Packages
import os
import pandas as pd

### Set working directory
from _set_directory import main_folder
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import output_folder
from _set_directory import appendix_output_folder


#%%      Importing Data      %%#
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%      Data Wrangling      %%#

# Keep key variables
df_export = df_observed[['wage1_c', 'wage1_n', 'P1_c', 'P1_n']]

# Keep key years
df_export.drop(index=range(1950,1977), inplace=True)
df_export.drop(index=range(2020,2023), inplace=True)

# Create College wage premium variable
df_export['College Wage Premium'] = df_export['wage1_c']/df_export['wage1_n'] - 1

# Renate columns in helpful way
df_export.rename(columns={'wage1_c':'Real Earnings, College', 
                    'wage1_n':'Real Earnings, Non-college', 
                    'P1_c':'Employment Rate, College', 
                    'P1_n':'Employment Rate, Non-college'},
                 inplace=True)


#%%      Data Export      %%#
os.chdir(output_folder)
df_export.to_excel("fmzz_fig1.xlsx")


#%% Return to code directory #%%
os.chdir(code_folder)