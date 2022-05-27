#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 18:23:52 2022

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


#%% Time Series Graphs #%%

## Define groups
# Outcomes
outcomes = ['Offered', 'Eligible for']
# Populations
populations = ['Total Population',
               'ESHI Dependents',
               'those without ESHI',
               'Uninsured Population']
# Demographics
demographics = ['Total',
                'College',
                'Non-College']
# Define range of years
years = range(2014,2022)

## Helpful Dictionaries
# Outcomes to variable names
outcomes2variables_Dict = {'Offered': 'ESHI_offered', 
                           'Eligible for': 'ESHI_eligible'}
# Population to identifier
populations2weight_Dict = {'Total Population': 1,
                           'ESHI Dependents': df['ESHI_dependent'],
                           'those without ESHI': (1-df['ESHI']),
                           'Uninsured Population': (1-df['HI'])}

## Loop to calcualte stats over time and graph them
os.chdir(output_folder)
#Loop through relevant populations  
for population in populations:
    pop_weight = populations2weight_Dict[population]
    
    #Loop through outcomes  
    for outcome in outcomes:
        outcome_var = outcomes2variables_Dict[outcome]
        
        #Define Variables
        variables = [f'Share {outcome} ESHI, {demo}' for demo in demographics]
        
        #Create Dataframe
        data = pd.DataFrame(index=years, columns=variables)

        #Loop through demographics        
        for demo in demographics:
            
            #Loop through years 
            for year in years:
                year_dummy = 1*(df['YEAR']==year)         
                data.loc[year, f'Share {outcome} ESHI, {demo}'] = \
                            np.average(df[outcome_var], \
                                weights=df['ASECWT']*year_dummy*df['FTFY']*df[demo]*pop_weight)
        
        #Plot results for this population-outcome
        plt.plot(data.iloc[:,0], color='black', marker='.')
        plt.plot(data.iloc[:,1], color='indianred', marker='.')
        plt.plot(data.iloc[:,2], color='steelblue', marker='.')
        plt.ylim([0,1])
        plt.title(f'Share {outcome} ESHI among {population}', fontsize=14)
        plt.legend(demographics)
        plt.grid(axis='y', color='gainsboro')
        plt.savefig(f'{outcome} among {population} Over Time.png', dpi=500)
        plt.clf() 

os.chdir(code_folder)