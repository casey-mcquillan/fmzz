#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 12:21:14 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
import numpy as np

### Set working directory and folders
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
os.chdir(code_folder)


#%% Import Data #%%
os.chdir(data_folder)
df = pd.read_csv('cps_00029.csv')


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

# Define sex
df['Female'] = 1*(df['SEX']==2)
df['Male'] = 1-df['Female']

# Define Health Insurance
df['ESHI_own'] = 1*(df['GRPOWNLY']==2)
df['ESHI_dependent'] = 1*(df['GRPDEPLY']==2)

# Constant column
df['Total'] = 1


#%% Inflation Adjust #%%
# Adjust wages to be in 2019 dollars
os.chdir(data_folder)
price_data = pd.read_csv('PCEPI_data.csv', index_col=0)
for year in data.index:
    adj_factor = price_data.loc[year, 'PCEPI Adjustment Factor (2019 Dollars)']
    for var in ['wage1_c_m', 'wage1_n_m', 'wage1_c_f', 'wage1_n_f']:
        data.loc[year, var] = adj_factor*data.loc[year, var]


#%% Create Dataframe by year #%%

# Define range of years
years = range(1975,2021)

# Define variables
variables = ['N', 'N_college', 'N_FTFY', 'N_college_FTFY',
                    'P1_c', 'P1_n',
                    'P1_c_m', 'P1_n_m', 'P1_c_f', 'P1_n_f',
                    'wage1_c', 'wage1_n',
                    'wage1_c_m', 'wage1_n_m', 'wage1_c_f', 'wage1_n_f',
                    'share_workers1_c', 'share_workers1_c_m', 'share_workers1_c_f',
                    'share_workers1_n', 'share_workers1_n_m', 'share_workers1_n_f',
                    'share_pop_c', 'share_pop_c_m', 'share_pop_c_f',
                    'share_pop_n', 'share_pop_n_m', 'share_pop_n_f',
                    'Share ESHI policyholders']

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

    ## Employment Rates
    data.loc[year,'P1_c'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['College'])    
    data.loc[year,'P1_n'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['Non-College'])
    data.loc[year,'P1_c_m'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['College']*df['Male'])
    data.loc[year,'P1_n_m'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['Non-College']*df['Male'])
    data.loc[year,'P1_c_f'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['College']*df['Female'])
    data.loc[year,'P1_n_f'] = np.average(df['FTFY'], \
                                        weights=df['ASECWT']*year_dummy*df['Non-College']*df['Female'])
    
    ## Wage Data
    data.loc[year,'wage1_c'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['College']*df['FTFY'])
    data.loc[year,'wage1_n'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['Non-College']*df['FTFY'])
    data.loc[year,'wage1_c_m'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['College']*df['Male']*df['FTFY'])
    data.loc[year,'wage1_n_m'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['Non-College']*df['Male']*df['FTFY'])
    data.loc[year,'wage1_c_f'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['College']*df['Female']*df['FTFY'])
    data.loc[year,'wage1_n_f'] = np.average(df['INCWAGE'], \
                                            weights=df['ASECWT']*year_dummy*df['Non-College']*df['Female']*df['FTFY'])

    ## Share of FTFY workforce
    data.loc[year,'share_workers1_c'] = np.average(df['College']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_c_m'] = np.average(df['College']*df['Male']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_c_f'] = np.average(df['College']*df['Female']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_n'] = np.average((1-df['College'])*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_n_m'] = np.average((1-df['College'])*df['Male']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])
    data.loc[year,'share_workers1_n_f'] = np.average((1-df['College'])*df['Female']*df['FTFY'], 
                                                    weights=df['ASECWT']*year_dummy*df['FTFY'])

    ## Share of Population        
    data.loc[year,'share_pop_c'] = np.average(df['College'], 
                                                    weights=df['ASECWT']*year_dummy)
    data.loc[year,'share_pop_c_m'] = np.average(df['College']*df['Male'], 
                                                    weights=df['ASECWT']*year_dummy)
    data.loc[year,'share_pop_c_f'] = np.average(df['College']*df['Female'], 
                                                    weights=df['ASECWT']*year_dummy)
    data.loc[year,'share_pop_n'] = np.average((1-df['College']), 
                                                    weights=df['ASECWT']*year_dummy)
    data.loc[year,'share_pop_n_m'] = np.average((1-df['College'])*df['Male'], 
                                                    weights=df['ASECWT']*year_dummy)
    data.loc[year,'share_pop_n_f'] = np.average((1-df['College'])*df['Female'], 
                                                    weights=df['ASECWT']*year_dummy)

    ## Share of FTFY workers that are ESHI policyholders
    if year >= 1995:
        # Share ESHI 
        data.loc[year,'Share ESHI policyholders'] = np.average(df['ESHI_own'], \
                                                               weights=df['ASECWT']*year_dummy*df['FTFY'])

        
#%% Export Data #%%
os.chdir(data_folder)
data_export = data[['N', 'N_college', 'N_FTFY', 'N_college_FTFY',
                    'P1_c', 'P1_n',
                    'P1_c_m', 'P1_n_m', 'P1_c_f', 'P1_n_f',
                    'wage1_c', 'wage1_n',
                    'wage1_c_m', 'wage1_n_m', 'wage1_c_f', 'wage1_n_f',
                    'share_workers1_c', 'share_workers1_c_m', 'share_workers1_c_f',
                    'share_workers1_n', 'share_workers1_n_m', 'share_workers1_n_f',
                    'share_pop_c', 'share_pop_c_m', 'share_pop_c_f',
                    'share_pop_n', 'share_pop_n_m', 'share_pop_n_f',
                    'Share ESHI policyholders']]
data_export.to_csv('RC2_clean_ASEC_data_bySex.csv')
