#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 16:45:59 2022

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
for var in ['EDUC', 'UHRSWORK1', 'CLASSWKR']:
    df = df[[not np.isnan(x) for x in df[var]]]
df = df[[not x in [0,1,999] for x in df['EDUC']]]
df = df[df['CLASSWKR']!=99]

# Drop self-employed workers
df = df[[(not x in [10,13,14,29]) for x in df['CLASSWKR']]]

# Drop years before 2019 where data is unavailable
df = df[df['YEAR'] >= 2019]

#Adjust year bc survey data corresponds to prev year
#df['YEAR'] = df['YEAR'] - 1
'''
For this analysis, it is not helpful since HIOFFER and HIELIGIBLE
are asked about current jobs
'''

# Define college attendance
df['College'] = \
    [int(x in [110, 120, 121, 122, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']

## Define FTFY
# Last year
hours_requirement =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement =  1*(df['WKSWORK2'] >= 4)
df['FTFY_LY'] = hours_requirement * weeks_requirement
# This year
hours_requirement = 1*(df['UHRSWORK1']>=35)
fulltime_status = 1*(df['WKSTAT']<=11)
df['FTFY'] = hours_requirement * fulltime_status

# Define Health Insurance
df['HI'] = 1*(df['ANYCOVNW']==1)
df['Public HI'] =   1*(df['PUBCOVNW']==2)
df['Public HI (Medicaid)'] =   1*(df['HIMCAIDNW']==2)
df['Public HI (Medicare)'] =   1*(df['HIMCARENW']==2)
df['Private HI'] =   1*(df['PRVTCOVNW']==2)
df['ESHI_own'] = 1*(df['GRPOWNNW']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPNW']==2)
df['ESHI'] = 1*(df['GRPOWNNW']==2) + \
    1*((1-1*(df['GRPOWNNW']==2))*(1*df['GRPDEPNW']==2))
df['ESHI_offered'] = 1*(df['HIOFFER']==2) + \
    1*((1-1*(df['HIOFFER']==2))*(1*df['GRPOWNLY']==2))
df['ESHI_eligible'] = 1*(df['HIELIG']==2) + \
    1*((1-1*(df['HIELIG']==2))*(1*df['GRPOWNLY']==2))
df['Other Private'] = df['Private HI'] - df['ESHI']
df['HI Other'] = df['HI'] - df['ESHI']
df['No HI'] = 1 - df['HI']

# Constant column
df['Total'] = 1


#%% Calculate Stats #%%

## Define groups
# Outcomes
outcomes = ['Offered', 'Eligible for']
# Populations
populations = ['Population',
               'ESHI Dependents',
               'those without ESHI',
               'those with Public HI',
               'Uninsured']
# Demographics
demographics = ['Total',
                'College',
                'Non-College']

## Helpful Dictionaries
# Outcomes to variable names
outcomes2variables_Dict = {'Offered': 'ESHI_offered', 
                           'Eligible for': 'ESHI_eligible'}
# Population to identifier
populations2weight_Dict = {'Population': 1,
                           'ESHI Dependents': df['ESHI_dependent'],
                           'those without ESHI': (1-df['ESHI']),
                           'those with Public HI': df['Public HI'],
                           'Uninsured': (1-df['HI'])}

#Define Variables
variables = [f'Share {outcome} ESHI, {demo}' 
                 for demo in demographics 
                 for outcome in outcomes]
    
#Create Dataframe
data = pd.DataFrame(index=populations, columns=variables)

## Loop to calcualte stats over time and graph them
os.chdir(output_folder)
#Loop through outcomes  
for outcome in outcomes:
    outcome_var = outcomes2variables_Dict[outcome]
      
    #Loop through relevant populations  
    for population in populations:
        pop_weight = populations2weight_Dict[population]
        
        #Loop through demographics        
        for demo in demographics:
                            
            data.loc[population, f'Share {outcome} ESHI, {demo}'] = \
                        np.average(df[outcome_var], \
                            weights=df['ASECWT']*df['FTFY']*df[demo]*pop_weight)
        
#%% Clustered Bar Graphs #%%

#Switch to output folder
os.chdir(output_folder)
        
#labels for bar graph          
labels = ['Total',
            'ESHI Dependents',
            'Non-ESHI',
            'Public HI',
            'Uninsured']

#Loop through demographics        
for demo in demographics:
            
    offered_data = data[f'Share Offered ESHI, {demo}']
    eligible_data = data[f'Share Eligible for ESHI, {demo}']
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, offered_data, width, label='Offered')
    rects2 = ax.bar(x + width/2, eligible_data, width, label='Eligible')
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title(f'Share Offered and Eligible for ESHI, {demo}')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim([0,1] )
    ax.legend()
    
    fig.tight_layout()

    plt.grid(axis='y', color='gainsboro')
    plt.savefig(f'Offered and Eligle for {demo}.png', dpi=500)
    plt.clf() 
    