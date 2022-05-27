#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 17:48:57 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%% 
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)


#%% Occupation Definitions #%%
occ_code_high = list(range(4,37+1)) + \
                list(range(43,200+1)) + \
                list(range(243,258+1)) + \
                list(range(203,235+1)) + \
                list(range(417,423+1))

occ_code_med = list(range(274,283+1)) + \
                list(range(303,389+1)) + \
                list(range(628,799+1))
                
occ_code_low = list(range(803,889+1)) + \
                list(range(558,599+1)) + \
                list(range(503,549+1)) + \
                list(range(405,408+1)) + \
                [415] + \
                list(range(425,427+1)) + \
                list(range(448,455+1)) + \
                list(range(433,444+1)) + \
                list(range(457,458+1)) + \
                list(range(459,467+1)) + \
                [468] + \
                list(range(469,472+1)) + \
                list(range(445,447+1)) + \
                list(range(473,498+1)) + \
                list(range(614,617+1))
    
#%% Define Function #%%

def occ90_sorting(code):
    
    if code in occ_code_high: 
        return "High"
    
    elif code in occ_code_med:
        return "Medium"

    elif code in occ_code_med:
        return "Low"

    else: return "."

#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00026.csv')


#%% Data Wrangling #%%
#Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['WKSWORK2']!=9]
df = df[df['CLASSWLY']!=99]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWLY']]]

#Adjust year bc survey data corresponds to prev year
df['YEAR'] = df['YEAR'] - 1

# Define college attendance
df['College'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']

# Define working
hours_requirement =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement * weeks_requirement

# Define Health Insurance
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['ESHI_eligible'] = 1*(df['HIELIG']==2) + \
    1*((1-1*(df['HIELIG']==2))*(1*df['GRPOWNLY']==2))
    
# Constant column
df['Total'] = 1


#%% Occupational Sorting #%%

#Drop periods before ESHI_dep and ESHI_own are available
df = df[df['YEAR'] >= 1995]
df['Skill Group'] = "."


import time
program_starts = time.time()


skill2codes_Dict= {'High':occ_code_high,
                    'Medium':occ_code_med,
                    'Low': occ_code_low}

for skill_group in ['High', 'Medium', 'Low']:
    df[skill_group] = 0
    occ_codes = skill2codes_Dict[skill_group]
    for occ_code in occ_codes:
        df[skill_group] = df[skill_group] + (1*df['OCC90LY']==occ_code)

end_time = time.time()
print(end_time-program_starts)


### Checking how well this does
df['occ_sorted'] = df['High'] + df['Medium'] + df['Low']
#Number of FTFY workers wihtout sorting
np.sum((1-df['occ_sorted'])*(df['FTFY']))



#%% Calculate by Year #%%

# Define range of years
years = range(1995,2021)

# Define variables
variables = ['Share High Skill',
             'Share Medium Skill',
             'Share Low Skill',
             'Share ESHI policyholders (High-Skill)',
             'Share ESHI policyholders (Medium-Skill)',
             'Share ESHI policyholders (Low-Skill)',
             'Share Eligible for ESHI (High-Skill)',
             'Share Eligible for ESHI (Medium-Skill)',
             'Share Eligible for ESHI (Low-Skill)']

# Create dataframe
data = pd.DataFrame(index=years, columns=variables)

# Loop through years to create dataframe
for year in years:
    year_dummy = 1*(df['YEAR']==year)
    
    for skill_group in ['High', 'Medium', 'Low']:
        
        # Share of FTFY Workers
        data.loc[year,f'Share {skill_group} Skill'] = \
            np.average(df[skill_group], \
                           weights=df['ASECWT']*year_dummy*df['FTFY'])
                
        # Share ESHI Policyholders
        data.loc[year,f'Share ESHI policyholders ({skill_group}-Skill)'] = \
            np.average(df['ESHI_own'], \
                           weights=df['ASECWT']*year_dummy*df['FTFY']*df[skill_group])

        # Share ESHI 
        if year >= 2013:
            data.loc[year,f'Share Eligible for ESHI ({skill_group}-Skill)'] = \
                np.average(df['ESHI_eligible'], \
                               weights=df['ASECWT']*year_dummy*df['FTFY']*df[skill_group])   

os.chdir(data_folder)
data_export = data
data_export.to_csv('ESHI_by_occupationGroup.csv')    
    
    