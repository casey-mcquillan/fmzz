#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s
Created on Mon Jan  9 23:31:36 2023
@author: caseymcquillan
"""
#%%  Preamble: Import packages #%%  
import os as os

#%% Set working directory #%%clear 
from _set_directory import code_folder
os.chdir(code_folder)


#%%  1. Clean Data  for Main Analysis #%%  

# Clean PCE price data
exec(open("1a_pull_PCEPI.py").read())

# Pull OECD Population Data
exec(open("1b_pull_OECD_data.py").read())

# Clean ASEC Data
exec(open("1c_clean_ASEC_data.py").read())

# Compile Observed Data from ASEC and OECD
exec(open("1d_compile_observed_data.py").read())

# Compile Observed Data for Cost Counterfactual
exec(open("1e_Constructing_CCF.py").read())


#%%  2. Generate Main Tables #%% 

# Generate Table 1:Summarty Statistics
exec(open("2a_SummaryStats.py").read())

# Generate Table 3: Equilibrium Comparison
exec(open("2b_EquilibriumComparison.py").read())

# Generate Table 4: Sensitivity Analysis for Equilibrium Comparison 
exec(open("2c_EquilibriumComparison_Robustness.py").read())

# Generate Table 5: Changes over Time
exec(open("2d_CounterfactualGrowth.py").read())

# Generate Table 6: Sensitivity Analysis for Changes over Time
exec(open("2e_CounterfactualGrowth_Robustness.py").read())

# Generate Table 7: Equilibrium Comparison with Cost Counterfactual
exec(open("2f_EquilibriumComparison_CCF.py").read())


#%%  Robustness Check 1: Alternative College Definition #%%  

### Clean and Compile Data
# Clean ASEC Data with College defined as Some College or More
exec(open("RC1a_clean_ASEC_data.py").read())

# Compile Observed Data from ASEC and OECD with Some College or More
exec(open("RC1b_compile_observed_data.py").read())

### Generate Tables
# Generate Appendix Table 1: Summary Stats with Some College or More
exec(open("RC1c_SummaryStats.py").read())

# Generate Appendix Table 2: Equilibrium Comparison with Some College or More
exec(open("RC1d_EquilibriumComparison.py").read())

# Generate Appendix Table 3: Changes over Time with Some College or More
exec(open("RC1e_CounterfactualGrowth.py").read())


#%%  Robustness Check 2: Decomposing Effects by Sex #%%

### Clean and Compile Data
# Clean ASEC Data with disaggregated sex variables
exec(open("RC2a_clean_ASEC_data_bySex.py").read())

# Compile Observed Data from ASEC and OECD with disaggregated sex variables
exec(open("RC2b_compile_observed_data_bySex.py").read())

### Generate Tables
# Generate Appendix Table 4: Equilibrium Comparison (Baseline, aggregate, and by sex)
exec(open("RC2c_EquilibriumComparison_bySex.py").read())

# Generate Appendix Table 5: Changes over Time by Sex
exec(open("RC2d_CounterfactualGrowth_bySex.py").read())
