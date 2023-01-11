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
    
    
#%%  Clean Data  for Main Analysis #%%  

# Clean ASEC Data
os.chdir(code_folder)
exec(open("clean_ASEC_data.py").read())

# Pull OECD Population Data
os.chdir(code_folder)
exec(open("OECD_data_pull.py").read())

# Compile Observed Data
os.chdir(code_folder)
exec(open("compile_observed_data.py").read())


#%%  Generate Main Tables #%% 

# Generate Table 1:  
os.chdir(code_folder)
exec(open("summary_stats.py").read())

# Generate Table XX:  
os.chdir(code_folder)
exec(open("EquilibriumComparison.py").read())

# Generate Table XX:  
os.chdir(code_folder)
exec(open("EquilibriumComparison_Robustness.py").read())

# Generate Table XX:  
os.chdir(code_folder)
exec(open("CounterfactualGrowth.py").read())

# Generate Table XX:  
os.chdir(code_folder)
exec(open("CounterfactualGrowth_Robustness.py").read())

# Generate Table XX:  
os.chdir(code_folder)
exec(open("CostCounterfactual.py").read())


#%%  Appendix: Alternative College Definition #%%  




#%%  Appendix: Decomposing Effects by Sex #%%  