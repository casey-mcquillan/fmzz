#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 11:08:03 2023
@author: caseymcquillan
"""
#%%  Preamble: Import packages #%%  
### Import Packages
import os
import pandas as pd

### Set working directory #%%
from _set_directory import code_folder
from _set_directory import data_folder


#%%  Importing Data #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('clean_OECD_data_54.csv', index_col='year')
ASEC_data = pd.read_csv('clean_ASEC_data_54.csv', index_col=0)

# Import time series data on wages:
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)

# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'epop_ratio': OECD_data['Employment Rate (25-54)']/100,
                'pop_count': OECD_data['Population (25-54)'],
                'share_pop_c': ASEC_data['share_pop_c (weighted)'],
                'share_workers1_c': ASEC_data['share_workers1_c (weighted)'],
                'wage1_c': ASEC_data['wage1_c (weighted)'],
                'wage1_n': ASEC_data['wage1_n (weighted)'],
                'P1_c': ASEC_data['P1_c (weighted)'],
                'P1_n': ASEC_data['P1_n (weighted)'],
                'tau_fullcoverage': premium_data['Avg Enr Cost'],
                'tau_baseline': premium_data['Avg Enr Cost']*ASEC_data.loc[2019,'Share ESHI policyholders (weighted)'],
                'Share ESHI policyholders':ASEC_data['Share ESHI policyholders (weighted)'],
                'Share ESHI policyholders, College':ASEC_data['Share ESHI policyholders, College (weighted)'],
                'Share ESHI policyholders, Non-college':ASEC_data['Share ESHI policyholders, Non-college (weighted)']
            })


#%%  Data Export #%%
## Select relevant variables
data_export = df_observed

## Export data
os.chdir(data_folder)
data_export.to_csv('observed_data_54.csv')


#%% Return to code directory #%%
os.chdir(code_folder)

