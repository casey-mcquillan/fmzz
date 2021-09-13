#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 15:44:23 2021

@author: caseymcquillan
"""


#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
ACS_data_folder = data_folder + '/ACS Educational Attainment Data'

os.chdir(code_folder)


#%% Data Cleaning #%%

# Set up dataframe for ACS data
variables_ACS = ['pop_25plus', 'pop_25plus_college', 'pop_65plus', 'pop_65plus_college', 
             'share_25plus_c', 'share_65plus_c']
variables_output = ['pop_25_65', 'pop_25_65_college', 'share_pop_c']
variables = variables_ACS + variables_output
years = range(2010, 2020)
df = pd.DataFrame(index=years,columns=variables)

# Import codes by year for available variables
os.chdir(data_folder)
ACS_codes_by_year = pd.read_excel('ACS_codes_by_year.xlsx', index_col='Variables')

# Loop through each year to make calculation
os.chdir(ACS_data_folder)
for year in years:
    
    # Load data file and metadata file
    meta_data = pd.read_csv('ACSST1Y' + str(year) + '.S1501_metadata_2021-07-23T063149.csv')
    census_data = pd.read_csv('ACSST1Y' + str(year) + '.S1501_data_with_overlays_2021-07-23T063149.csv')
    
    # Create dictionary to map variables to ID
    variable_ID_dict= {var:ACS_codes_by_year.loc[var, year] for var in variables_ACS}
    # Create dictionary to map ID to column name
    ID_code_dict = {meta_data.loc[i,'id']:meta_data.loc[i,'GEO_ID'] for i in range(len(meta_data))}
    
    # Loop through variables in dictionary to pull into data frame
    for var in variable_ID_dict.keys():
        ID = variable_ID_dict[var]
        # If this is value is NA, then skip
        if pd.isna(ID): continue
        
        #Input value into dataframe    
        code = ID_code_dict[ID]
        value = census_data.loc[1, code]
        df.loc[year, var] = float(census_data.loc[1, code])
        
    # Modify based on whether percentage or number is available for different years
    if pd.isna(df.loc[year, 'share_25plus_c']):
        df.loc[year, 'share_25plus_c'] = 100*df.loc[year, 'pop_25plus_college'] / df.loc[year, 'pop_25plus']
    else: 
        df.loc[year, 'pop_25plus_college'] = df.loc[year, 'pop_25plus'] *(df.loc[year, 'share_25plus_c']/100)

    if pd.isna(df.loc[year, 'share_65plus_c']):
        df.loc[year, 'share_65plus_c'] = 100*df.loc[year, 'pop_65plus_college'] / df.loc[year, 'pop_65plus']
    else: 
        df.loc[year, 'pop_65plus_college'] = df.loc[year, 'pop_65plus'] *(df.loc[year, 'share_65plus_c']/100)

# Create variables for 25-65 demographic
df.loc[:, 'pop_25_65'] = df.loc[:, 'pop_25plus'] - df.loc[:, 'pop_65plus']
df.loc[:, 'pop_25_65_college'] = df.loc[:, 'pop_25plus_college'] - df.loc[:, 'pop_65plus_college']
df.loc[:, 'share_pop_c'] = df.loc[:, 'pop_25_65_college'] / df.loc[:, 'pop_25_65']

'''
NOTE:
For years 2010-2012, the dictionary used for ID_code_dict is somewhat fragile 
because the ID is 'Total!!Estimate!!Bachelor's degree or higher' and this ID
shows up multiple times in the meta data, but it works because it shows up last
for the 65+ demo that we care about.    
'''

#%%  Visualization: share_pop_c for 25 and older versus ages 25-64 #%%
## Import graph packages
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

## Graph 1: Series Comparison
plt.plot(df['share_pop_c'], \
         label= 'Ages 25-64')
plt.plot(df['share_25plus_c']/100, \
         label= '25 and Older')
plt.title('Share of Population with Bachelor\'s Degree or More')
plt.ylim([0,0.4])
plt.legend()
plt.show()



#%%  Data Export #%%
## Select relevant variables
data_export = df[['share_pop_c']]

## Export data
os.chdir(data_folder)
data_export.to_csv('share_pop_c.csv')
