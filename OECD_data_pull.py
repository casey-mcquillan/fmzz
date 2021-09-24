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

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/output"
os.chdir(code_folder)

#%%  Data Wrangling #%%
#Create data frame and pull data
data = pd.DataFrame()
data_pull = fred.get_series('LNS12300060', observation_start='1950-01-01')

#Populate data frame with relevant data
data['epop'] = data_pull
data['month'] = pd.to_datetime(data_pull.index).strftime('%m')
data['year'] = pd.to_datetime(data_pull.index).strftime('%Y')

#Collapse data by year
data = data.groupby('year').mean()


#%%  Data Wrangling #%%
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


#%%  Data Check: Compare OECD and BLS data #%%
## Import graph packages
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

## Graph 1: Series Comparison of Employment-Population Ratio
plt.plot(data['BLS: Employment-Population Ratio (25-54)'],  \
         label= 'BLS: Employment-Population Ratio (25-54)')
plt.plot(data['Employment Rate (25-54)'], \
         label= 'OECD: Employment Rate (25-54)')
plt.title('Comparing BLS and OECD Data')
plt.legend()
os.chdir(output_folder)
plt.savefig('compare_epop.png', dpi=500)
plt.show()

## Graph 2: Series Difference
plt.plot(data['Employment Rate (25-54)']-data['Employment-Population Ratio (25-54)'])
plt.title('Difference in BLS and OECD Data (pp)')
plt.show()

## Graph 3: Series Comparison of Population
plt.plot(data['BLS: Population (25-54)']*1000,  \
         label= 'BLS')
plt.plot(data['Population (25-54)'], \
         label= 'OECD')
plt.title('Population (25-54)')
plt.legend()
os.chdir(output_folder)
plt.savefig('compare_pop.png', dpi=500)
plt.show()

#%%  Data Export #%%
## Collapse data by year
data = data.groupby('year').mean()

## Select relevant variables
data_export = data[['Employment Rate (25-64)','Population (25-64)']]

## Export data
os.chdir(code_folder)
data_export.to_csv('OECD_data.csv')


## Graph 4: Employment Rate Series
plt.plot(data_export.index, data_export['Employment Rate (25-64)'])
plt.title('Employment-Population Ratio (25-64)')
plt.gca().xaxis.set_major_locator(plt.MultipleLocator(5))
os.chdir(output_folder)
plt.savefig('epop.png', dpi=500)
plt.show()

## Graph 5: Population Series
plt.plot(data_export.index, data_export['Population (25-64)'])
plt.title('Population (25-64)')
plt.gca().xaxis.set_major_locator(plt.MultipleLocator(5))
os.chdir(output_folder)
plt.savefig('pop.png', dpi=500)
plt.show()
