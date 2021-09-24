#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 23:09:14 2021

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
ACS_data = pd.read_csv('share_pop_c.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Patrick")
income_data = pd.read_excel('income_series.xlsx', index_col=0)
worker_share_data = pd.read_excel('share_series.xlsx', index_col=0)
premium_data = pd.read_excel('premiums_series.xlsx', index_col=0)

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
                'share_pop_c': ACS_data['share_pop_c'],
                'share_workers1_c': worker_share_data['Bachelor\'s Degree or More']/100,
                'wage_c': income_data['Bachelor\'s Degree or More'],
                'wage_n': income_data['Less than a Bachelor\'s Degree'],
                'tau_high': premium_data['Average Costo per Enrollee'],
                'tau_med': premium_data['Average Cost to Employer'] 
            })
            #'tau_low': xxx,


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


#%%  Calibration Over Time #%% 

# Parameter assumptions:
alpha_c=1
alpha_n=1

# Outcomes to track
y_series = []

# Loop through and calibrate model each year
years = range(2008, 2019)
for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage_c'], 
                w1_n=df_observed.loc[year, 'wage_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                epop_ratio1=df_observed.loc[year, 'epop_ratio'],
                pop_count=df_observed.loc[year, 'pop_count'])
    
    #Make sure there are no NANs in model before calibration
    if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
        print("NAN value entered into calibration model for:")
        for var in vars(model).keys():
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))
        break
    
    #Calibrate Model
    model.calibrate()
    
    #Collect relevant statistics
    college_wage_premium1 = (model.w1_c - model.w1_n)
    college_wage_premium2 = (model.w2_c - model.w2_n)
    y = (college_wage_premium2 - college_wage_premium1) / college_wage_premium1
    y_series.append(y)