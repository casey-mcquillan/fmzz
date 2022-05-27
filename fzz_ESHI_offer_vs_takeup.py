#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 10:34:58 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np


# Import plotting packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False


### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/ESHI Offer"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00021.csv')


#%% Data Wrangling #%%
#Drop invalid responses
for var in ['EDUC', 'WKSWORK2', 'UHRSWORKLY', 'CLASSWLY', 'INCWAGE', 'HIOFFER', 'HIELIG']:
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
df['HI'] = 1*(df['ANYCOVNW']==1)
#df['Public HI'] =   1*(df['PUBCOVLY']==2)
#df['Public HI (Medicaid)'] =   1*(df['HIMCAIDLY']==2)
#df['Public HI (Medicare)'] =   1*(df['HIMCARELY']==2)
#df['Private HI'] =   1*(df['PRVTCOVLY']==2)
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)
df['ESHI'] = 1*(df['GRPOWNLY']==2) + \
    1*((1-1*(df['GRPOWNLY']==2))*(1*df['GRPDEPLY']==2))
df['ESHI_offered'] = 1*(df['HIOFFER']==2) + \
    1*((1-1*(df['HIOFFER']==2))*(1*df['GRPOWNLY']==2))
df['ESHI_eligible'] = 1*(df['HIELIG']==2) + \
    1*((1-1*(df['HIELIG']==2))*(1*df['GRPOWNLY']==2))
#df['Other Private'] = df['Private HI'] - df['ESHI']
#df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']

# Constant column
df['Total'] = 1




#%% Take Up Versus Offering #%%

### Offering
# Universe: Respondents who were not covered by employer-based health insurance plans who are employed and not self-employed.
# Share no
offer_no = np.average(1*(df['HIOFFER']==1),
                      weights=df['FTFY']*(1-(df['HIOFFER']==99)))

# Share yes
offer_yes = np.average(1*(df['HIOFFER']==2),
                       weights=df['FTFY']*(1-(df['HIOFFER']==99)))


### Eligibility
#Universe: Respondents who were not covered by employer-based health insurance plans who are employed and not self-employed whose employer offers health insurance benefits to any employees.
# Share no
eligible_no = np.average(1*(df['HIELIG']==1),
                         weights=df['ASECWT']*df['FTFY']*(1-(df['HIELIG']==99)))

# Share yes
eligible_yes = np.average(1*(df['HIELIG']==2),
                          weights=df['ASECWT']*df['FTFY']*(1-(df['HIELIG']==99)))

