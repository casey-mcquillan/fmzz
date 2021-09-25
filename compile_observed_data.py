#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 22:34:36 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)

### Import calibration class
from fzz_calibration import calibration_model 


#%%  Importing Data #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('share_pop_c_ASEC.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Patrick")
income_data = pd.read_excel('income_series.xlsx', index_col=0)
worker_share_data = pd.read_excel('share_series.xlsx', index_col=0)
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)

# Modify to format for college and non-college groups
worker_share_data['Some College, but no Bachelor\'s Degree'] = \
    worker_share_data['Some College or More'] - worker_share_data['Bachelor\'s Degree or More']

worker_share_data['Less than a Bachelor\'s Degree'] = \
    worker_share_data['Some College, but no Bachelor\'s Degree'] + worker_share_data['HS Degree or Less']

income_data['Some College, but no Bachelor\'s Degree'] = \
    (income_data['Some College or More'] * (worker_share_data['Some College or More']/100) \
    - income_data['Bachelor\'s Degree or More'] * (worker_share_data['Bachelor\'s Degree or More']/100)) \
    / ((worker_share_data['Some College or More']/100) - (worker_share_data['Bachelor\'s Degree or More']/100))

income_data['Less than a Bachelor\'s Degree'] = \
    income_data['Some College, but no Bachelor\'s Degree'] \
        * (worker_share_data['Some College, but no Bachelor\'s Degree']/worker_share_data['Less than a Bachelor\'s Degree']) \
    + income_data['HS Degree or Less'] \
        * (worker_share_data['HS Degree or Less']/worker_share_data['Less than a Bachelor\'s Degree'])

# Create dataframe with necessary observed variables
df_observed = pd.DataFrame({
                'epop_ratio': OECD_data['Employment Rate (25-64)']/100,
                'pop_count': OECD_data['Population (25-64)'],
                'share_pop_c': ASEC_data['share_pop_c'],
                'share_workers1_c': worker_share_data['Bachelor\'s Degree or More']/100,
                'wage_c': income_data['Bachelor\'s Degree or More'],
                'wage_n': income_data['Less than a Bachelor\'s Degree'],
                'tau_high': premium_data['Average Cost per Enrollee'],
                'tau_med': premium_data['Average Cost to Employer per enrollee'],
                'tau_low': premium_data['Employer cost X Take Up'],
            })


#%%  Visualizing Data: Gut Check #%%  
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

groups = ['Bachelor\'s Degree or More',
       'Some College or More', 'HS Degree or Less',
       'Some College, but no Bachelor\'s Degree',
       'Less than a Bachelor\'s Degree']
for group in groups:
    plt.plot(income_data[group], label= group)
    plt.title("Income")
plt.legend()
plt.show()

for group in groups:
    plt.plot(worker_share_data[group], label= group)
    plt.title("Shares")
plt.legend()
plt.show()


#%%  Data Export #%%
## Select relevant variables
data_export = df_observed

## Export data
os.chdir(data_folder)
data_export.to_csv('observed_data.csv')