#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 14:03:16 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
os.chdir(code_folder)


#%%  Importing Data #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('CPS_ASEC_clean_bySex.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Emily")
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)

# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'pop_count': OECD_data['Population (25-64)'],
                'P1_c': ASEC_data['P1_c'],
                'P1_n': ASEC_data['P1_n'],
                'P1_c_m': ASEC_data['P1_c_m'],
                'P1_n_m': ASEC_data['P1_n_m'],
                'P1_c_f': ASEC_data['P1_c_f'],
                'P1_n_f': ASEC_data['P1_n_f'],
                'wage1_c': ASEC_data['wage1_c'],
                'wage1_n': ASEC_data['wage1_n'],
                'wage1_c_m': ASEC_data['wage1_c_m'],
                'wage1_n_m': ASEC_data['wage1_n_m'],
                'wage1_c_f': ASEC_data['wage1_c_f'],
                'wage1_n_f': ASEC_data['wage1_n_f'],
                'share_workers1_c': ASEC_data['share_workers1_c'],
                'share_workers1_c_m': ASEC_data['share_workers1_c_m'],
                'share_workers1_c_f': ASEC_data['share_workers1_c_f'],
                'share_workers1_n': ASEC_data['share_workers1_n'],
                'share_workers1_n_m': ASEC_data['share_workers1_n_m'],
                'share_workers1_n_f': ASEC_data['share_workers1_n_f'],
                'share_pop_c': ASEC_data['share_pop_c'],
                'share_pop_c_m': ASEC_data['share_pop_c_m'],
                'share_pop_c_f': ASEC_data['share_pop_c_f'],
                'share_pop_n': ASEC_data['share_pop_n'],
                'share_pop_n_m': ASEC_data['share_pop_n_m'],
                'share_pop_n_f': ASEC_data['share_pop_n_f'],
                "Share ESHI policyholders": ASEC_data["Share ESHI policyholders"],
                'tau_high': premium_data['Avg Enr Cost'],
                'tau_baseline': premium_data['Avg Enr Cost']*ASEC_data.loc[2019,'Share ESHI policyholders'],
                'tau_low': premium_data['Avg Emp Cost']*ASEC_data.loc[2019,'Share ESHI policyholders']
            })


#%%  Data Export #%%
## Select relevant variables
data_export = df_observed

## Export data
os.chdir(data_folder)
data_export.to_csv('observed_data_bySex.csv')


