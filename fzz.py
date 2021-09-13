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

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)

### Import calibration class
from fzz_calibration import economy 


#%%  Calibration Over Time #%%  
os.chdir(data_folder)

# Import data series for calibration
OECD_data = pd.read_csv('OECD_data.csv', index_col='year')
ACS_data = pd.read_csv('share_pop_c.csv', index_col=0)

x_var = []

years = range(2010, 2020)
for year in years:
    var1 = OECD_data.loc[year, 'Employment Rate (25-64)'] / 100
    var2 = OECD_data.loc[year, 'Population (25-64)']
    var3 = ACS_data.loc[year, 'share_pop_c']
    

    model = economy(alpha_c=1, alpha_n=1,
                tau=8569, w1_c=88381, w1_n=47373, 
                share_workers1_c=1.2*var3, share_pop_c=var3, 
                epop_ratio1=var1, pop_count=var2)
    model.calibrate()
    
    
    college_wage_premium1 = (model.w1_c - model.w1_n)
    college_wage_premium2 = (model.w2_c - model.w2_n)
    x = (college_wage_premium2 - college_wage_premium1) / college_wage_premium1
    x_var.append(x)
    
    
    
#%%  Visualization: #%%
## Import graph packages
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

## Graph 1: Series Comparison
plt.plot(years, x_var)
plt.title('Pct. Change in College Wage Premium')
#plt.legend()
plt.show()