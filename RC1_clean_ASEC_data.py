#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 16:47:40 2021
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
exec(open("__set_directory.py").read())


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

##############################################################################
# Define college attendance as Some College or More
df['College'] = \
    [int(x in [80, 90, 100, 110, 120, 121, 122, 81, 91, 92, 111, 123, 124, 125]) for x in df['EDUC']]
df['Non-College'] = 1-df['College']
###############################################################################

# Define working
hours_requirement =  1*(df['UHRSWORKLY'] >= 35)
weeks_requirement =  1*(df['WKSWORK2'] >= 4)
df['FTFY'] = hours_requirement * weeks_requirement

# Define Health Insurance
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)

# Constant column
df['Total'] = 1


#%% Create Dataframe by year #%%

# Define range of years
years = range(1975,2021)

# Define variables
variables = ['N', 'N_college', 'N_FTFY', 'N_college_FTFY',
                    'share_pop_c', 'share_pop_c (weighted)', 
                    'share_workers1_c', 'share_workers1_c (weighted)',
                    'P1_c', 'P1_c (weighted)',
                    'P1_n', 'P1_n (weighted)',
                    'wage1_c', 'wage1_c (weighted)',
                    'wage1_n', 'wage1_n (weighted)',
                    'Share ESHI policyholders', 
                    'Share ESHI policyholders (weighted)',
                    'Share ESHI policyholders, College', 
                    'Share ESHI policyholders, College (weighted)',
                    'Share ESHI policyholders, Non-college', 
                    'Share ESHI policyholders, Non-college (weighted)',
                    'Share ESHI dependents',
                    'Share ESHI dependents (weighted)']

# Create dataframe
data = pd.DataFrame(index=years, columns=variables)

# Loop through years to create dataframe
for year in years:
    year_dummy = 1*(df['YEAR']==year)
        
    ### Calculations
    ## Number of observations
    data.loc[year,'N'] = np.sum(df['Total']*year_dummy)
    data.loc[year,'N_college'] = np.sum(df['College']*year_dummy)
    data.loc[year,'N_FTFY'] = np.sum(df['FTFY']*year_dummy)
    data.loc[year,'N_college_FTFY'] = np.sum(df['College']*df['FTFY']*year_dummy)
    
    ## College Share of population
    data.loc[year,'share_pop_c'] = np.average(df['College'], \
                                                weights=year_dummy)
    data.loc[year,'share_pop_c (weighted)'] = np.average(df['College'], \
                                                weights=df['ASECWT']*year_dummy)
    
    ## College Share of FTFY workforce
    data.loc[year,'share_workers1_c'] = np.average(df['College']*df['FTFY'], \
                                                    weights=year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_c (weighted)'] = np.average(df['College']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    ## Employment Rates
    data.loc[year,'P1_c'] = np.average(df['College']*df['FTFY'], \
                                       weights=year_dummy*df['College'])
    data.loc[year,'P1_c (weighted)'] = np.average(df['College']*df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['College'])
    
    data.loc[year,'P1_n'] = np.average(df['Non-College']*df['FTFY'], \
                                       weights=year_dummy*df['Non-College'])
    data.loc[year,'P1_n (weighted)'] = np.average(df['Non-College']*df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['Non-College'])


    ## Wage Data
    data.loc[year,'wage1_c'] = np.average(df['INCWAGE']*df['College']*df['FTFY'], \
                                          weights=year_dummy*df['College']*df['FTFY'])
    data.loc[year,'wage1_c (weighted)'] = np.average(df['INCWAGE']*df['College']*df['FTFY'], \
                                            weights=df['ASECWT']*year_dummy*df['College']*df['FTFY'])
    data.loc[year,'wage1_n'] = np.average(df['INCWAGE']*df['Non-College']*df['FTFY'], \
                                          weights=year_dummy*df['Non-College']*df['FTFY'])
    data.loc[year,'wage1_n (weighted)'] = np.average(df['INCWAGE']*df['Non-College']*df['FTFY'], \
                                            weights=df['ASECWT']*year_dummy*df['Non-College']*df['FTFY'])

    ## Share of FTFY workers that are ESHI policyholders
    if year >= 1995:
        # Share ESHI 
        data.loc[year,'Share ESHI policyholders'] = \
            np.average(df['ESHI_own']*df['FTFY'], \
                       weights=year_dummy*df['FTFY'])
        data.loc[year,'Share ESHI policyholders (weighted)'] = \
            np.average(df['ESHI_own']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df['FTFY'])
                
        # Share ESHI policyholders by college status
        data.loc[year,'Share ESHI policyholders, College'] = \
            np.average(df['ESHI_own']*df['FTFY']*df['College'], \
                       weights=year_dummy*df['FTFY']*df['College'])
        data.loc[year,'Share ESHI policyholders, College (weighted)'] = \
            np.average(df['ESHI_own']*df['FTFY']*df['College'], \
                       weights=df['ASECWT']*year_dummy*df['FTFY']*df['College']) 
                
        data.loc[year,'Share ESHI policyholders, Non-college'] = \
            np.average(df['ESHI_own']*df['FTFY']*df['Non-College'], \
                       weights=year_dummy*df['FTFY']*df['Non-College'])
        data.loc[year,'Share ESHI policyholders, Non-college (weighted)'] = \
            np.average(df['ESHI_own']*df['FTFY']*df['Non-College'], \
                       weights=df['ASECWT']*year_dummy*df['FTFY']*df['Non-College'])
        
        # Share ESHI Dependents
        data.loc[year,'Share ESHI dependents'] = \
            np.average(df['ESHI_dependent']*df['FTFY'], \
                       weights=year_dummy*df['FTFY'])
        data.loc[year,'Share ESHI dependents (weighted)'] = \
            np.average(df['ESHI_dependent']*df['FTFY'], \
                       weights=df['ASECWT']*year_dummy*df['FTFY'])  
    

#%% Export Data #%%
os.chdir(data_folder)
data_export = data[['N', 'N_college', 'N_FTFY', 'N_college_FTFY',
                    'share_pop_c', 'share_pop_c (weighted)', 
                    'share_workers1_c', 'share_workers1_c (weighted)',
                    'P1_c', 'P1_c (weighted)',
                    'P1_n', 'P1_n (weighted)',
                    'wage1_c', 'wage1_c (weighted)',
                    'wage1_n', 'wage1_n (weighted)',
                    'Share ESHI policyholders', 
                    'Share ESHI policyholders (weighted)',
                    'Share ESHI policyholders, College', 
                    'Share ESHI policyholders, College (weighted)',
                    'Share ESHI policyholders, Non-college', 
                    'Share ESHI policyholders, Non-college (weighted)',
                    'Share ESHI dependents',
                    'Share ESHI dependents (weighted)']]
data_export.to_csv('RC1_clean_ASEC_data.csv')
