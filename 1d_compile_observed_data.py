#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 22:34:36 2021
@author: caseymcquillan
"""
#%%  Preamble: Import packages #%%  
### Import Packages
import os
import pandas as pd
import numpy as np


#%% Set working directory #%%
from _set_directory import main_folder
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import output_folder
from _set_directory import appendix_output_folder


#%%  Importing Data #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('clean_OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('clean_ASEC_data.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Emily")
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)

# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'epop_ratio': OECD_data['Employment Rate (25-64)']/100,
                'pop_count': OECD_data['Population (25-64)'],
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
data_export.to_csv('observed_data.csv')
