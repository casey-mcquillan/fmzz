#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 11:03:44 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")


### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)


#%%  Importing Data #%%  
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%  Graph observed values over time #%% 


variables = ['epop_ratio', 'pop_count', 'share_pop_c', 'share_workers1_c', 'wage_c',
       'wage_n', 'tau_high', 'tau_med', 'tau_low']


for var in variables:
    plt.plot(df_observed[var])
    plt.title(var)
    plt.show()

df_extrapolated =pd.DataFrame(index = range(1950,2021))
for tau in ['tau_high', 'tau_med', 'tau_low']:
    start_year = 1996
    end_year = 2018
    T = end_year - start_year
    
    tau_0 = df_observed.loc[start_year, tau]
    tau_T = df_observed.loc[end_year, tau]
    
    avg_growth = (tau_T/tau_0)**(1/T)
    
    df_extrapolated.loc[start_year, tau] = tau_0
    for i in range(start_year+1,2031):
        tau_prev = df_extrapolated.loc[i-1, tau]
        df_extrapolated.loc[i, tau] = tau_prev * avg_growth

for tau in ['tau_high', 'tau_med', 'tau_low']:
    plt.plot(df_observed[tau])
    plt.plot(df_extrapolated[tau])
    plt.title(tau)
    plt.show()