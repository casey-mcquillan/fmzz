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


#%% Set working directory #%%
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder = main_folder+"/output/Tables/"


#%%  1. Clean Data  for Main Analysis #%%  

# Clean ASEC Data
os.chdir(code_folder)
exec(open("1a_pull_PCEPI.py").read())

# Pull OECD Population Data
os.chdir(code_folder)
exec(open("1b_pull_OECD_data.py").read())

# Clean ASEC Data
os.chdir(code_folder)
exec(open("1c_clean_ASEC_data.py").read())

# Compile Observed Data from ASEC and OECD
os.chdir(code_folder)
exec(open("1d_compile_observed_data.py").read())

# Compile Observed Data for Cost Counterfactual
os.chdir(code_folder)
exec(open("1e_Constructing_CCF.py").read())


#%%  2. Generate Main Tables #%% 

# Generate Table 1:  
os.chdir(code_folder)
exec(open("2a_SummaryStats.py").read())

# Generate Table 3:  
os.chdir(code_folder)
exec(open("2b_EquilibriumComparison.py").read())

# Generate Table 4:  
os.chdir(code_folder)
exec(open("2c_EquilibriumComparison_Robustness.py").read())

# Generate Table 5:  
os.chdir(code_folder)
exec(open("2d_CounterfactualGrowth.py").read())

# Generate Table 6:  
os.chdir(code_folder)
exec(open("2e_CounterfactualGrowth_Robustness.py").read())

# Generate Table 7:  
os.chdir(code_folder)
exec(open("2f_EquilibriumComparison_CCF.py").read())


#%%  Robustness Check 1: Alternative College Definition #%%  

### Clean Data
# Clean ASEC Data
os.chdir(code_folder)
exec(open("RC1a_clean_ASEC_data.py").read())

# Compile Observed Data from ASEC and OECD
os.chdir(code_folder)
exec(open("RC1b_compile_observed_data.py").read())

### Generate Tables
# Generate Appendix Table 1:  
os.chdir(code_folder)
exec(open("RC1c_SummaryStats.py").read())

# Generate Appendix Table 2:  
os.chdir(code_folder)
exec(open("RC1d_EquilibriumComparison.py").read())

# Generate Appendix Table 3:  
os.chdir(code_folder)
exec(open("RC1e_CounterfactualGrowth.py").read())


#%%  Robustness Check 2: Decomposing Effects by Sex #%%

### Clean Data
# Clean ASEC Data
os.chdir(code_folder)
exec(open("RC2a_clean_ASEC_data_bySex.py").read())

# Compile Observed Data from ASEC and OECD
os.chdir(code_folder)
exec(open("RC2b_compile_observed_data_bySex.py").read())

### Generate Tables
# Generate Appendix Table 4:  
os.chdir(code_folder)
exec(open("RC2c_EquilibriumComparison_bySex.py").read())

# Generate Appendix Table 5:  
os.chdir(code_folder)
exec(open("RC2d_CounterfactualGrowth_bySex.py").read())