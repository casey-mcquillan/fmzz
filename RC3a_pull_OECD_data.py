#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 11:09:04 2023
@author: caseymcquillan
"""
#%%  Preamble: Import packages #%%  
import os as os
import pandas as pd

### Set working directory
from _set_directory import code_folder
from _set_directory import data_folder

### Set up Fred for data pull
from fredapi import Fred
from _fred_api_key import fred_api_key
fred = Fred(api_key=fred_api_key)


#%%      Constructing the Data      %%#
##  Define series for data pull
start_time = '1950-01-01'
series_dict ={'Employment Rate (25-54)':'LREM25TTUSM156S',
                'Population (25-54)':'LFWA25TTUSM647N'}
series_name, series_code = zip(*series_dict.items())

##  Pull data
data = pd.DataFrame()
for name in series_name:
        code = series_dict[name]
        data_pull = fred.get_series(code, observation_start=start_time)
        data = pd.concat([data, data_pull], axis=1)
data.columns=series_name   

##  Creating additional variables
#data['Employment Level (25-54)'] = data['Employment Rate (25-54)']*data['Population (25-54)']
#data['Employment Level (55-64)'] = data['Employment Rate (55-64)']*data['Population (55-64)']

#data['Employment Level (25-64)'] = data['Employment Level (25-54)']+data['Employment Level (55-64)']
#data['Population (25-64)'] = data['Population (25-54)']+data['Population (55-64)']
#data['Employment Rate (25-64)'] = data['Employment Level (25-64)']/data['Population (25-64)']

data['month'] = pd.to_datetime(data.index).strftime('%m')
data['year'] = pd.to_datetime(data.index).strftime('%Y')


#%%      Exporting the Data      %%#
## Collapse data by year
data = data.groupby('year').mean()

## Select relevant variables
data_export = data[['Employment Rate (25-54)','Population (25-54)']]

## Export data
os.chdir(data_folder)
data_export.to_csv('clean_OECD_data_54.csv')


#%% Return to code directory #%%
os.chdir(code_folder)

