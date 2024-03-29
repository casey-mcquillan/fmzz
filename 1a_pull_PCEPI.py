#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 16:33:14 2021

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

#%%  Data Wrangling #%%
#Create data frame and pull data
data = pd.DataFrame()
data_pull = fred.get_series('PCEPI', observation_start='1962-01-01')

#Populate data frame with relevant data
data['PCE Price Index'] = data_pull
data['month'] = pd.to_datetime(data_pull.index).strftime('%m')
data['year'] = pd.to_datetime(data_pull.index).strftime('%Y')

#Collapse data by year
data = data.groupby('year').mean()

#Determine base year and calculate index
base_year = str(2019)
data[f'PCEPI Adjustment Factor ({base_year} Dollars)'] = \
    data.loc[base_year, 'PCE Price Index'] / data['PCE Price Index']
    
## Export data
os.chdir(data_folder)
data.to_csv('PCEPI_data.csv')


#%% Return to code directory #%%
os.chdir(code_folder)