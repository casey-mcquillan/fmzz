#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 22:44:00 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder_graphs = main_folder+"/output/Graphs/Cost Counterfactual"
os.chdir(code_folder)

#%%      Calculating Counterfactual Paths:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%      Establishing Baseline:      %%#

# Parameter assumptions:
year1 = 1977
year2 = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'

#%%      Calculating Counterfactual Paths:      %%#

### No Growth CCF
years = [1977,1987] + list(range(1996, 2020))
df_observed['tau_CCF_NoGrowth'] = np.nan
for year in years:
    df_observed.loc[year,'tau_CCF_NoGrowth'] = df_observed.loc[year1,tau_baseline]

### Canada GDP-Share CCF
# Import CSV File
os.chdir(data_folder)
df_canada_CF = pd.read_csv('health_spending.csv', delim_whitespace=True)

# Data Wrangling
df_canada_CF=df_canada_CF.pivot(index='year', columns='country')
df_canada_CF.columns=df_canada_CF.columns.droplevel(0)
df_canada_CF['Canada-US Ratio'] = df_canada_CF['Canada']/df_canada_CF['United States']

# Calculate Canada Cost Counterfactual 1
theta_US_1977 = df_canada_CF.loc[1977,'United States']
theta_CAN_1977 = df_canada_CF.loc[1977,'Canada']

years = [1977,1987] + list(range(1996, 2020))
df_observed['tau_CCF_Canada1'] = np.nan
for year in years:
    theta_US_year = df_canada_CF.loc[year,'United States']
    theta_CAN_year = df_canada_CF.loc[year,'Canada']
    scale = (theta_US_1977 + (theta_CAN_year-theta_CAN_1977)) / theta_US_year
    df_observed.loc[year,'tau_CCF_Canada1'] = \
        df_observed.loc[year,tau_baseline]*scale


# Calculate Canada Cost Counterfactual 2    
years = [1977,1987] + list(range(1996, 2020))
df_observed['tau_CCF_Canada2'] = np.nan
for year in years:
    if year ==1977: scale=1
    else: scale=df_canada_CF.loc[year,'Canada-US Ratio']
    df_observed.loc[year,'tau_CCF_Canada2'] = \
        df_observed.loc[year,tau_baseline]*scale


#%% Export Data #%%
os.chdir(data_folder)
df_observed.to_csv('observed_data_CCF.csv')   


#%%      Output Graph with CF Tau:      %%#
        
# Import Packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False

# Plot
plt.plot(df_observed['tau_baseline'].dropna(), label='Observed',
         marker='.', ms=5, color='black')
plt.plot(df_observed['tau_CCF_Canada1'].dropna(), label='Canada Counterfactual 1',
         marker='.', ms=5, color='maroon')
plt.plot(df_observed['tau_CCF_Canada2'].dropna(), label='Canada Counterfactual 2',
         marker='.', ms=5, color='indianred')
plt.plot(df_observed['tau_CCF_NoGrowth'].dropna(), label='No Growth Counterfactual',
         marker='.', ms=5, color='navy')
plt.ylim([0,8000])
plt.title("Cost of ESHI and Counterfactuals", fontsize=14)
plt.ylabel('2019 USD')
plt.legend()
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(axis='y', color='gainsboro')
plt.tick_params(bottom=True, left=True)
os.chdir(output_folder_graphs)
plt.savefig('tau_CCF.png', dpi=500)
plt.clf()