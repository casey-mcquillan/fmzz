#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 13:52:22 2022

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
output_path = main_folder+'/output/Graphs/Analysis by Sex'


#%%      Import Data:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)
df_observed_bySex = pd.read_csv('observed_data_bySex.csv', index_col=0)


#%%      Figures:      %%#

# Import necessary Packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False

# Change path to output folder
os.chdir(output_path)

## Graphs by Group ###
#  Employment Rate
plt.plot(df_observed['P1_c'], label="College", 
                 color='firebrick', marker='.')
plt.plot(df_observed['P1_n'], label="Non-college", 
                 color='royalblue', marker='.')
plt.legend()
plt.ylim([0.2,1.0])
plt.title("Employment Rate by Group", fontsize=14)
plt.grid(axis='y', color='gainsboro')
plt.savefig('EmploymentRate.png', dpi=500)
plt.clf() 

#  Wages
plt.plot(df_observed['wage1_c'], label="College", 
                 color='firebrick', marker='.')
plt.plot(df_observed['wage1_n'], label="Non-college", 
                 color='royalblue', marker='.')
plt.legend()
plt.ylim([20000,120000])
plt.title("Wages by Group", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(axis='y', color='gainsboro')
plt.savefig('wages.png', dpi=500)
plt.clf() 


## Graphs by Group and Sex ###
#  Employment Rate
plt.plot(df_observed_bySex['P1_c_m'], label="College, Male", 
                 color='darkred', marker='.')
plt.plot(df_observed_bySex['P1_c_f'], label="College, Female", 
                 color='salmon', marker='.')
plt.plot(df_observed_bySex['P1_n_m'], label="Non-college, Male", 
                 color='midnightblue', marker='.')
plt.plot(df_observed_bySex['P1_n_f'], label="Non-college, Female", 
                 color='lightskyblue', marker='.')
plt.legend()
plt.ylim([0.2,1.0])
plt.title("Employment Rate by Group and Sex", fontsize=14)
plt.grid(axis='y', color='gainsboro')
plt.savefig('EmploymentRate_bySex.png', dpi=500)
plt.clf() 

#  Wages
plt.plot(df_observed_bySex['wage1_c_m'], label="College, Male", 
                 color='darkred', marker='.')
plt.plot(df_observed_bySex['wage1_c_f'], label="College, Female", 
                 color='salmon', marker='.')
plt.plot(df_observed_bySex['wage1_n_m'], label="Non-college, Male", 
                 color='midnightblue', marker='.')
plt.plot(df_observed_bySex['wage1_n_f'], label="Non-college, Female", 
                 color='lightskyblue', marker='.')
plt.legend()
plt.ylim([20000,120000])
plt.title("Wages by Group", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.grid(axis='y', color='gainsboro')
plt.savefig('wages_bySex.png', dpi=500)
plt.clf() 
