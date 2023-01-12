#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 10:53:30 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)


#%%  Importing Data #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ASEC_data = pd.read_csv('CPS_ASEC_clean.csv', index_col=0)

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
                'share_pop_c': ASEC_data['share_pop_c (weighted)'],
                'share_workers1_c': ASEC_data['share_workers1_c (weighted)'],
                'wage1_c': ASEC_data['wage1_c (weighted)'],
                'wage1_n': ASEC_data['wage1_n (weighted)'],
                'P1_c': ASEC_data['P1_c (weighted)'],
                'P1_n': ASEC_data['P1_n (weighted)'],
                'tau_high': premium_data['Average Cost per Enrollee'],
                'tau_med': premium_data['Average Cost to Employer per enrollee'],
                'tau_low': premium_data['Employer cost X Take Up'],
            })


#%%  Summary Table Over Time #%% 
os.chdir(code_folder)
from fzz_calibration_old import calibration_model as calibration_model_old

# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years
years = [1977,1987] + list(range(1996, 2019))
P1_c= pd.DataFrame(index=years, columns=['value'])
P1_n= pd.DataFrame(index=years, columns=['value'])
for year in years:
    
    #Define and calibrate model
    model = calibration_model_old(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
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
        continue
    
    #Calibrate Model
    model.calibrate()
    
    P1_c.loc[year, 'value'] = model.P1_c
    P1_n.loc[year, 'value'] = model.P1_n
    
    
#%%  Summary Table Over Time #%% 
os.chdir(code_folder)
from fzz_calibration import calibration_model

# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years
years = [1977,1987] + list(range(1996, 2019))
epop_ratio1 = pd.DataFrame(index=years, columns=['value'])
for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                pop_count=df_observed.loc[year, 'pop_count'])


        #Make sure there are no NANs in model before calibration
    if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
        print("NAN value entered into calibration model for:")
        for var in vars(model).keys():
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))
        continue
    
    #Calibrate Model
    model.calibrate()
    
    epop_ratio1.loc[year, 'value'] = model.epop_ratio1
    


#%%  Summary Table Over Time #%% 
plt.title("Share of Workers with College Education")
plt.plot(df_observed['share_workers1_c'], label="New Measure")
plt.plot(worker_share_data['Bachelor\'s Degree or More']/100, label="Old Measure")
plt.legend()
plt.show()

plt.title("Average Wage for Worker with College Education")
plt.plot(df_observed['wage1_c'], label="New Measure")
plt.plot(income_data['Bachelor\'s Degree or More'], label="Old Measure")
plt.legend()
plt.show()

plt.title("Average Wage for Worker without College Education")
plt.plot(df_observed['wage1_n'], label="New Measure")
plt.plot(income_data['Less than a Bachelor\'s Degree'], label="Old Measure")
plt.legend()
plt.show()

plt.title("LFP for Worker with College Education")
plt.plot(df_observed['P1_c'], label="New Measure")
plt.plot(P1_c, label="Old Measure")
plt.legend()
plt.show()

plt.title("LFP for Worker without College Education")
plt.plot(df_observed['P1_n'], label="New Measure")
plt.plot(P1_n, label="Old Measure")
plt.legend()
plt.show()

plt.title("Employment-to-Population Ratio")
plt.plot(epop_ratio1, label="New Measure")
plt.plot(OECD_data['Employment Rate (25-64)']/100, label="Old Measure")
plt.legend()
plt.show()