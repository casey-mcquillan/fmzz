#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 23:31:09 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
import os as os
import pandas as pd
from fredapi import Fred
fred = Fred(api_key='d6e26ca3fc202a8c68409b1c78708331')


#%%  Data Wrangling #%%
#Create data frame and pull data
data = pd.DataFrame()
data_pull = fred.get_series('LNS12300060', observation_start='1950-01-01')

#Populate data frame with relevant data
data['epop'] = data_pull
data['month'] = pd.to_datetime(data_pull.index).strftime('%m')
data['year'] = pd.to_datetime(data_pull.index).strftime('%Y')

#Collapse data by year
data = data.groupby('year').mean()