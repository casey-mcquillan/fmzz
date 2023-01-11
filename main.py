#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s
Created on Mon Jan  9 23:31:36 2023

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
    
    
#%%  1. Clean Data  for Main Analysis #%%  

# Clean ASEC Data
os.chdir(code_folder)
exec(open("clean_ASEC_data.py").read())

# Pull OECD Population Data
os.chdir(code_folder)
exec(open("pull_OECD_data.py").read())

# Compile Observed Data
os.chdir(code_folder)
exec(open("compile_observed_data.py").read())


#%%  2. Generate Main Tables #%% 

# Generate Table 1:  
os.chdir(code_folder)
exec(open("summary_stats.py").read())

# Generate Table 3:  
os.chdir(code_folder)
exec(open("EquilibriumComparison.py").read())

# Generate Table 4:  
os.chdir(code_folder)
exec(open("EquilibriumComparison_Robustness.py").read())

# Generate Table 5:  
os.chdir(code_folder)
exec(open("CounterfactualGrowth.py").read())

# Generate Table 6:  
os.chdir(code_folder)
exec(open("CounterfactualGrowth_Robustness.py").read())

# Generate Table 7:  
os.chdir(code_folder)
exec(open("CostCounterfactual.py").read())


#%%  Appendix: Alternative College Definition #%%  


# Clean ASEC Data
os.chdir(code_folder)
exec(open("clean_ASEC_data.py").read())

# Generate Appendix Table 1:  
os.chdir(code_folder)
exec(open("RC1_SummaryStats.py").read())

#%%  Appendix: Decomposing Effects by Sex #%%  