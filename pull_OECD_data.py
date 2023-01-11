#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 23:31:09 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
from fredapi import Fred
fred = Fred(api_key='d6e26ca3fc202a8c68409b1c78708331')

### Set working directory and folders
exec(open("__set_directory.py").read())


#%%      Constructing the Data      %%#
##  Define series for data pull
start_time = '1950-01-01'
series_dict ={'BLS: Employment-Population Ratio (25-54)':'LNS12300060',
              'BLS: Population (25-54)': 'LNU00000060',
                'Employment Rate (25-54)':'LREM25TTUSM156S',
                'Population (25-54)':'LFWA25TTUSM647N',
                'Employment Rate (55-64)':'LREM55TTUSM156S',
                'Population (55-64)':'LFAC55TTUSM647N'}
series_name, series_code = zip(*series_dict.items())

##  Pull data
data = pd.DataFrame()
for name in series_name:
        code = series_dict[name]
        data_pull = fred.get_series(code, observation_start=start_time)
        data = pd.concat([data, data_pull], axis=1)
data.columns=series_name   

##  Creating additional variables
data['Employment Level (25-54)'] = data['Employment Rate (25-54)']*data['Population (25-54)']
data['Employment Level (55-64)'] = data['Employment Rate (55-64)']*data['Population (55-64)']

data['Employment Level (25-64)'] = data['Employment Level (25-54)']+data['Employment Level (55-64)']
data['Population (25-64)'] = data['Population (25-54)']+data['Population (55-64)']
data['Employment Rate (25-64)'] = data['Employment Level (25-64)']/data['Population (25-64)']

data['month'] = pd.to_datetime(data.index).strftime('%m')
data['year'] = pd.to_datetime(data.index).strftime('%Y')


#%%      Exporting the Data      %%#
## Collapse data by year
data = data.groupby('year').mean()

## Select relevant variables
data_export = data[['Employment Rate (25-64)','Population (25-64)']]

## Export data
os.chdir(data_folder)
data_export.to_csv('clean_OECD_data.csv')
