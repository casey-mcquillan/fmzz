#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 11:28:36 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Figures"
os.chdir(code_folder)

### Import calibration class
from fzz_calibration import calibration_model 


#%%  Importing Data #%%  
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Import time series data on wages, tau from Patrick Collard:
os.chdir(data_folder + "/Time Series from Patrick")
premium_data = pd.read_excel('premium_series.xlsx', index_col=0)


#%%  Summary Table Over Time #%% 
# Parameter assumptions:
alpha_c=1
alpha_n=1

#Output path and define years
years = [1977,1987] + list(range(1996, 2019))


outcome_variables = ['wage_premium1', 'wage_premium2',
             'wage_share1', 'wage_share2', 
             'share_workers1_c', 'share_workers2_c',
             'P1_c', 'P1_n', 'P2_c', 'P2_n',
             'w1_c', 'w1_n', 'w2_c', 'w2_n',
             'reduction_college_wage_premium',
             'reduction_college_wage_share']

df_results = pd.DataFrame(index=years, columns=outcome_variables)

for year in years:
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, 'tau_high'], 
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                pop_count=df_observed.loc[year, 'pop_count'])


    #Make sure there are no NANs in model before calibration
    if any(np.isnan([vars(model)[x] for x in vars(model).keys()])):
        print("NAN value entered into calibration model for:")
        for var in vars(model).keys():
            if np.isnan(vars(model)[var])==True: print("    "+var)
        print("for year: " + str(year))
        continue
    
    #Calibrate Model
    model.calibrate()
    
 
    df_results.loc[year,'wage_premium1'] = model.w1_c - model.w1_n
    df_results.loc[year,'wage_premium2'] = model.w2_c - model.w2_n
    df_results.loc[year,'wage_share1'] = model.w1_c * model.L1_c  \
                                            / (model.w1_c * model.L1_c + model.w1_n * model.L1_n)
    df_results.loc[year,'wage_share2'] = model.w2_c * model.L2_c  \
                                            / (model.w2_c * model.L2_c + model.w2_n * model.L2_n)
    df_results.loc[year,'share_workers1_c'] = model.share_workers1_c
    df_results.loc[year,'share_workers2_c'] = model.share_workers2_c
    df_results.loc[year,'P1_c'] = model.P1_c
    df_results.loc[year,'P1_n'] = model.P1_n
    df_results.loc[year,'P2_c'] = model.P2_c
    df_results.loc[year,'P2_n'] = model.P2_n
    df_results.loc[year,'w1_c'] = model.w1_c
    df_results.loc[year,'w1_n'] = model.w1_n
    df_results.loc[year,'w2_c'] = model.w2_c
    df_results.loc[year,'w2_n'] = model.w2_n
    df_results.loc[year,'reduction_college_wage_premium'] = \
        -100*((model.w2_c - model.w2_n) - (model.w1_c - model.w1_n))/(model.w1_c - model.w1_n)
    df_results.loc[year,'reduction_college_wage_share'] = \
        -100*((df_results.loc[year,'wage_share2']) - (df_results.loc[year,'wage_share1']))
    
    
#%%  Graphs #%% 
# Import necessary Packages
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")


# Change path to output folder
os.chdir(output_folder)

## Graphs ###
#  Share of population with a college degree
plt.plot(df_observed['share_pop_c'])
plt.ylim([0,0.5])
plt.title("Share of Population with Bachelor's Degree or More", fontsize=14)
plt.savefig('share_pop_c.png', dpi=500)
plt.clf() 


#  Share of workeforce with a college degree
plt.plot(df_observed['share_workers1_c'])
plt.ylim([0,0.5])
plt.title("Share of Workers with Bachelor's Degree or More", fontsize=14)
plt.savefig('share_workers_c_observed.png', dpi=500)
plt.clf() 

plt.plot(df_results['share_workers1_c'], label="Head Tax Equilibrium")
plt.plot(df_results['share_workers2_c'], label="Payroll Tax Equilibrium")
plt.legend()
plt.ylim([0,0.5])
plt.title("Share of Workers with Bachelor's Degree or More", fontsize=14)
plt.savefig('share_workers_c.png', dpi=500)
plt.clf() 


#  Both shares
plt.plot(df_observed['share_workers1_c'], label="Share of Workforce with College Degree")
plt.plot(df_observed['share_pop_c'], label="Share of Population with College Degree")
plt.legend()
plt.ylim([0,0.5])
plt.savefig('share_college.png', dpi=500)
plt.clf() 

#  Employment Rate
plt.plot(df_observed['P1_c'], label="College", color='darkred')
plt.plot(df_observed['P1_n'], label="Non-college", color='navy')
plt.legend()
plt.ylim([0.5,0.8])
plt.title("Labor Force Participation by Group", fontsize=14)
plt.savefig('LFP_observed.png', dpi=500)
plt.clf() 

plt.plot(df_results['P1_c'], label="Head Tax Equilibrium", color='darkred')
plt.plot(df_results['P2_c'], label="Payroll Tax Equilibrium", color='indianred')
plt.legend()
plt.ylim([0.65,0.8])
plt.title("Labor Force Participation for College Workers", fontsize=14)
plt.savefig('LFP_c.png', dpi=500)
plt.clf() 

plt.plot(df_results['P1_n'], label="Head Tax Equilibrium", color='navy')
plt.plot(df_results['P2_n'], label="Payroll Tax Equilibrium", color='steelblue')
plt.legend()
plt.ylim([0.5,0.70])
plt.title("Labor Force Participation for Non-college Workers", fontsize=14)
plt.savefig('LFP_n.png', dpi=500)
plt.clf() 

plt.plot(df_results['P1_c'], label="College, Head Tax", color='darkred')
plt.plot(df_results['P2_c'], label="College, Payroll Tax", color='indianred')
plt.plot(df_results['P1_n'], label="Non-college, Head Tax", color='navy')
plt.plot(df_results['P2_n'], label="Non-college, Payroll Tax", color='steelblue')
plt.legend()
plt.ylim([0.5,0.8])
plt.title("Labor Force Participation by Group", fontsize=14)
plt.savefig('LFP.png', dpi=500)
plt.clf() 


#  Wages
plt.plot(df_observed['wage1_c'], label="College", color='darkred')
plt.plot(df_observed['wage1_n'], label="Non-college", color='navy')
plt.legend()
plt.title("Wages by Group", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('wages_observed.png', dpi=500)
plt.clf() 

plt.plot(df_results['w1_c'], label="Head Tax Equilibrium", color='darkred')
plt.plot(df_results['w2_c'], label="Payroll Tax Equilibrium", color='indianred')
plt.legend()
plt.ylim([60000,100000])
plt.title("Wages for College Workers", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('wages_c.png', dpi=500)
plt.clf() 

plt.plot(df_results['w1_n'], label="Head Tax Equilibrium", color='navy')
plt.plot(df_results['w2_n'], label="Payroll Tax Equilibrium", color='steelblue')
plt.legend()
plt.ylim([40000,55000])
plt.title("Wages for Non-college Workers", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('wages_n.png', dpi=500)
plt.clf() 

plt.plot(df_results['w1_c'], label="College, Head Tax", color='darkred')
plt.plot(df_results['w2_c'], label="College, Payroll Tax", color='indianred')
plt.plot(df_results['w1_n'], label="Non-college, Head Tax", color='navy')
plt.plot(df_results['w2_n'], label="Non-college, Payroll Tax", color='steelblue')
plt.legend()
plt.ylim([40000,100000])
plt.title("Wages by Group", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('wages.png', dpi=500)
plt.clf() 


#  College wage premium
plt.plot(df_observed['wage1_c']-df_observed['wage1_n'])
plt.title("College Wage Premium", fontsize=14)
plt.savefig('college_wage_premium_observed.png', dpi=500)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('college_wage_premium_observed.png', dpi=500)
plt.clf() 

plt.plot(df_results['wage_premium1'], label="Head Tax Equilibrium")
plt.plot(df_results['wage_premium2'], label="Payroll Tax Equilibrium")
plt.legend()
plt.title("College Wage Premium", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('college_wage_premium.png', dpi=500)
plt.clf() 

plt.plot(df_results['reduction_college_wage_premium'])
plt.suptitle("Pct. Reduction in College Wage Premium", y=0.99, fontsize=14)
plt.title(r'(Head Tax $\Rightarrow$ Payroll tax)', fontsize=12)
plt.savefig('reduction_college_wage_premium.png', dpi=500)
plt.clf() 


#  College share
plt.plot(df_results['wage_share1'])
plt.title("College Share of Total Wage Bill", fontsize=14)
plt.savefig('wage_share_observed.png', dpi=500)
plt.clf() 

plt.plot(df_results['wage_share1'], label="Head Tax Equilibrium")
plt.plot(df_results['wage_share2'], label="Payroll Tax Equilibrium")
plt.title("College Share of Total Wage Bill", fontsize=14)
plt.legend()
plt.savefig('wage_share.png', dpi=500)
plt.clf() 

plt.plot(df_results['reduction_college_wage_share'])
plt.suptitle('PP. Reduction in College Share of Total Wage Bill', y=0.99, fontsize=14)
plt.title(r'(Head Tax $\Rightarrow$ Payroll tax)', fontsize=12)
plt.savefig('reduction_college_wage_share.png', dpi=500)
plt.clf() 


#  Tau parameters
plt.plot(df_observed['tau_high'].dropna(), label='Total Cost and Complete Take-up')
plt.plot(df_observed['tau_med'].dropna(), label='Cost to Employer and Complete Take-up')
plt.plot(df_observed['tau_low'].dropna(), label='Cost to Employer and Incomplete Take-up')
plt.legend()
plt.title("Cost of ESHI", fontsize=14)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
plt.savefig('tau.png', dpi=500)
plt.clf() 





