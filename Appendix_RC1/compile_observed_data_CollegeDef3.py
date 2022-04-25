#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 12:46:41 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed_RC1 = pd.read_csv('observed_data_RC1.csv', index_col=0)

### Creating df_observed based on College Definition 3
df_observed = pd.read_csv('observed_data.csv', index_col=0)
for var in ['share_pop_c', 'share_workers1_c', 'wage1_c', 'wage1_n', 'P1_c', 'P1_n']:
    df_observed[var] = df_observed_RC1[f'{var} [College Definition 3]']
    
    
#%%  Data Export #%%
## Select relevant variables
data_export = df_observed

## Export data
os.chdir(data_folder)
data_export.to_csv('observed_data_CollegeDef3.csv')

