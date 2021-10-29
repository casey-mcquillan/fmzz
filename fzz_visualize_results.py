#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 18:37:37 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

### Set working directory
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(code_folder)

### Import calibration class
from fzz_calibration import calibration_model 


#%%  Importing Data #%%  
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)
os.chdir(code_folder)


#%%  Varying Tau #%% 
# Parameter assumptions:
year = 2018
alpha_c, alpha_n, = 1, 1

# Parameter to be varied:
tau_params = np.linspace(0, 12000, 1201)

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Visualize Results'

#Define variables and empty dataframe for results
variables = ["Pct. Chg. in College Wage Premium (O to H)", 
             "Pct. Chg. in College Wage Premium (H to P)", 
             "Change in College Share of Wage Bill  (O to H)",
             "Change in College Share of Wage Bill  (H to P)"]
df_varying_tau = pd.DataFrame(index = tau_params, \
                              columns = variables)

#Loop through values of tau
for tau in tau_params:
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=tau, 
                w1_c=df_observed.loc[year, 'wage_c'], 
                w1_n=df_observed.loc[year, 'wage_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                epop_ratio1=df_observed.loc[year, 'epop_ratio'],
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

    #Calculate variables of interest
    pct_chg_wage_premium_01 = 100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n)
    pct_chg_wage_premium_12 = 100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
    pp_chg_wage_bill_01 = 100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))- \
                                   ((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n)))
    pp_chg_wage_bill_12 = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                   ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
        
    #Store variables
    df_varying_tau.loc[tau, "Pct. Chg. in College Wage Premium (O to H)"] = pct_chg_wage_premium_01
    df_varying_tau.loc[tau, "Pct. Chg. in College Wage Premium (H to P)"] = pct_chg_wage_premium_12
    df_varying_tau.loc[tau, "Change in College Share of Wage Bill  (O to H)"] = pp_chg_wage_bill_01
    df_varying_tau.loc[tau, "Change in College Share of Wage Bill  (H to P)"] = pp_chg_wage_bill_12

#Generate Graphs
os.chdir(output_path)

plt.figure(figsize=(6,4))
plt.plot(df_varying_tau["Pct. Chg. in College Wage Premium (O to H)"])
plt.xlabel(r'Value of $\tau$')
plt.ylabel("Pct. Chg. in College Wage Premium")
plt.ylim(-20,5)
plt.savefig('varyTau_1.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.plot(df_varying_tau["Pct. Chg. in College Wage Premium (H to P)"], color='maroon')
plt.xlabel(r'Value of $\tau$')
plt.ylabel("Pct. Chg. in College Wage Premium")
plt.ylim(-20,5)
plt.savefig('varyTau_2.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.plot(df_varying_tau["Change in College Share of Wage Bill  (O to H)"])
plt.xlabel(r'Value of $\tau$')
plt.ylabel("Change in College Share of Wage Bill")
plt.ylim(-4,4)
plt.savefig('varyTau_3.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.plot(df_varying_tau["Change in College Share of Wage Bill  (H to P)"], color='maroon')
plt.xlabel(r'Value of $\tau$')
plt.ylabel("Change in College Share of Wage Bill")
plt.ylim(-4,4)
plt.savefig('varyTau_4.png', dpi=500)
plt.clf()

os.chdir(code_folder)


#%%  Varying Alphas #%% 
# Parameter assumptions:
year = 2018
tau_param = 'tau_high'
N = 36

# Parameter to be varied:
alpha_range = np.linspace(0.25, 2, N)

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Visualize Results'

#Create arrays to store data
array_pct_chg_wage_premium_01 = np.empty([N,N])
array_pct_chg_wage_premium_12 = np.empty([N,N])
array_pp_chg_wage_bill_01 = np.empty([N,N])
array_pp_chg_wage_bill_12 = np.empty([N,N])

#Loop through pairs of alpha 
for i in range(N):
    alpha_c = alpha_range[i]
    
    for j in range(N):
        alpha_n = alpha_range[j]
    
        #Define and calibrate model
        model = calibration_model(alpha_c, alpha_n,
                    tau=df_observed.loc[year, tau_param], 
                    w1_c=df_observed.loc[year, 'wage_c'], 
                    w1_n=df_observed.loc[year, 'wage_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    epop_ratio1=df_observed.loc[year, 'epop_ratio'],
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
        
        #Calculate variables of interest
        pct_chg_wage_premium_01 = 100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n)
        pct_chg_wage_premium_12 = 100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
        pp_chg_wage_bill_01 = 100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))- \
                                       ((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n)))
        pp_chg_wage_bill_12 = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))
            
        #Store variables
        array_pct_chg_wage_premium_01[i,j] = pct_chg_wage_premium_01
        array_pct_chg_wage_premium_12[i,j] = pct_chg_wage_premium_12
        array_pp_chg_wage_bill_01[i,j] = pp_chg_wage_bill_01
        array_pp_chg_wage_bill_12[i,j] = pp_chg_wage_bill_12
        
#Generate Graphs
os.chdir(output_path)

plt.figure(figsize=(6,4))
plt.imshow(array_pct_chg_wage_premium_01, cmap='Blues', extent=[0.25,2,2,0.25])
plt.colorbar() 
plt.xlabel(r'$\alpha_N$')
plt.ylabel(r'$\alpha_C$')
plt.gca().invert_yaxis()
plt.yticks(np.arange(0.25, 2.01, step=0.25))
plt.savefig('varyAlpha_1.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.imshow(array_pct_chg_wage_premium_12, cmap='Reds', extent=[0.25,2,2,0.25])
plt.colorbar()
plt.xlabel(r'$\alpha_N$')
plt.ylabel(r'$\alpha_C$')
plt.gca().invert_yaxis()
plt.yticks(np.arange(0.25, 2.01, step=0.25))
plt.savefig('varyAlpha_2.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.imshow(array_pp_chg_wage_bill_01, cmap='Blues', extent=[0.25,2,2,0.25])
plt.colorbar()
plt.xlabel(r'$\alpha_N$')
plt.ylabel(r'$\alpha_C$')
plt.gca().invert_yaxis()
plt.yticks(np.arange(0.25, 2.01, step=0.25))
plt.savefig('varyAlpha_3.png', dpi=500)
plt.clf()

plt.figure(figsize=(6,4))
plt.imshow(array_pp_chg_wage_bill_12, cmap='Reds', extent=[0.25,2,2,0.25])
plt.colorbar()
plt.xlabel(r'$\alpha_N$')
plt.ylabel(r'$\alpha_C$')
plt.gca().invert_yaxis()
plt.yticks(np.arange(0.25, 2.01, step=0.25))
plt.savefig('varyAlpha_4.png', dpi=500)
plt.clf()

os.chdir(code_folder)


#%%  Varying Tau over Time #%% 
# Parameter assumptions:
alpha_c, alpha_n, = 1, 1

# Parameter to be varied:
years = [1977,1987] + list(range(1996, 2019))
tau_params = ['tau_high', 'tau_med', 'tau_low']
tau2specification_Dict ={'tau_high':'Total Cost and Complete Take-up',
                         'tau_med':'Cost to Employer and Complete Take-up',
                         'tau_low':'Cost to Employer and Incomplete Take-up'}

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Visualize Results'

#Define varibables
variables = ["Pct. Chg. in College Wage Premium (O to H)", 
             "Pct. Chg. in College Wage Premium (H to P)", 
             "Change in College Share of Wage Bill  (O to H)",
             "Change in College Share of Wage Bill  (H to P)"]

#Loop through values of tau and year
df_varying_tau_byYear = pd.DataFrame(columns = ['year', 'tau', 'variable', 'value'])

for tau in tau_params:
    for year in years:
        #Define and calibrate model
        model = calibration_model(alpha_c, alpha_n,
                    tau=df_observed.loc[year, tau], 
                    w1_c=df_observed.loc[year, 'wage_c'], 
                    w1_n=df_observed.loc[year, 'wage_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    epop_ratio1=df_observed.loc[year, 'epop_ratio'],
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
    
        #Calculate variables of interest
        pct_chg_wage_premium_01 = 100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n)
        pct_chg_wage_premium_12 = 100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
        pp_chg_wage_bill_01 = 100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))- \
                                       ((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n)))
        pp_chg_wage_bill_12 = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))

        #Create rows for dataframe and append them
        new_row1 = {'year':year, 'tau':tau, \
                    'variable':"Pct. Chg. in College Wage Premium (O to H)", \
                    'value':pct_chg_wage_premium_01}
            
        new_row2 = {'year':year, 'tau':tau, \
                    'variable':"Pct. Chg. in College Wage Premium (H to P)", \
                    'value':pct_chg_wage_premium_12}
        
        new_row3 = {'year':year, 'tau':tau, \
                    'variable':"Change in College Share of Wage Bill  (O to H)", \
                    'value':pp_chg_wage_bill_01}
            
        new_row4 = {'year':year, 'tau':tau, \
                    'variable':"Change in College Share of Wage Bill  (H to P)", \
                    'value':pp_chg_wage_bill_12}
        
        df_varying_tau_byYear = df_varying_tau_byYear.append(\
                    [new_row1, new_row2, new_row3, new_row4], ignore_index=True)
            
#Generate Graphs
os.chdir(output_path)

for var in variables:
    df_graph = df_varying_tau_byYear[df_varying_tau_byYear['variable']==var]

    plt.figure(figsize=(6,4))     
    for tau in tau_params:    
        df_series = df_graph[[x == tau for x in df_graph['tau']]]
        plt.plot(df_series['year'], df_series['value'], label=tau2specification_Dict[tau])
    plt.legend()
    plt.xlabel("Year")
    plt.title(var)
    if var == "Pct. Chg. in College Wage Premium (O to H)":
        plt.ylim(-1,1)
    plt.savefig('varyTau_byYear_'+str(variables.index(var) + 1)+'.png', dpi=500)
    plt.clf()  

os.chdir(code_folder)
    
            
 #%%  Varying alphas over Time #%% 
# Parameter assumptions:
tau_param = 'tau_high'

# Parameter to be varied:
years = [1977,1987] + list(range(1996, 2019))
alpha_values = [[1,1], [1.2,1.2], [0.8,0.8], [0.9,0.7]]

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Visualize Results'

#Define varibables
variables = ["Pct. Chg. in College Wage Premium (O to H)", 
             "Pct. Chg. in College Wage Premium (H to P)", 
             "Change in College Share of Wage Bill  (O to H)",
             "Change in College Share of Wage Bill  (H to P)"]

#Loop through values of tau and year
df_varying_alphas_byYear = pd.DataFrame(columns = ['year', 'alphas', 'variable', 'value'])

for alphas in alpha_values:      
    alpha_c, alpha_n, = alphas[0], alphas[1]
    
    for year in years:
        #Define and calibrate model
        model = calibration_model(alpha_c, alpha_n,
                    tau=df_observed.loc[year, tau_param], 
                    w1_c=df_observed.loc[year, 'wage_c'], 
                    w1_n=df_observed.loc[year, 'wage_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    epop_ratio1=df_observed.loc[year, 'epop_ratio'],
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
    
        #Calculate variables of interest
        pct_chg_wage_premium_01 = 100*((model.w1_c-model.w1_n)-(model.w0_c-model.w0_n))/(model.w0_c-model.w0_n)
        pct_chg_wage_premium_12 = 100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n)
        pp_chg_wage_bill_01 = 100*(((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))- \
                                       ((model.L0_c*model.w0_c)/(model.L0_c*model.w0_c + model.L0_n*model.w0_n)))
        pp_chg_wage_bill_12 = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))- \
                                       ((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))

        #Create rows for dataframe and append them
        new_row1 = {'year':year, 'alphas':alphas, \
                    'variable':"Pct. Chg. in College Wage Premium (O to H)", \
                    'value':pct_chg_wage_premium_01}
            
        new_row2 = {'year':year, 'alphas':alphas, \
                    'variable':"Pct. Chg. in College Wage Premium (H to P)", \
                    'value':pct_chg_wage_premium_12}
        
        new_row3 = {'year':year, 'alphas':alphas, \
                    'variable':"Change in College Share of Wage Bill  (O to H)", \
                    'value':pp_chg_wage_bill_01}
            
        new_row4 = {'year':year, 'alphas':alphas, \
                    'variable':"Change in College Share of Wage Bill  (H to P)", \
                    'value':pp_chg_wage_bill_12}
        
        df_varying_alphas_byYear = df_varying_alphas_byYear.append(\
                    [new_row1, new_row2, new_row3, new_row4], ignore_index=True)
            
#Generate Graphs
os.chdir(output_path)

for var in variables:
    df_graph = df_varying_alphas_byYear[df_varying_alphas_byYear['variable']==var]        
    
    plt.figure(figsize=(6,4))
    for alphas in alpha_values:    
        df_series = df_graph[[x == alphas for x in df_graph['alphas']]]
        plt.plot(df_series['year'], df_series['value'], label=str(alphas))
    plt.legend(title = r'$[\alpha_c, \alpha_c]$')
    plt.xlabel("Year")
    plt.title(var)
    plt.savefig('varyAlpha_byYear_'+str(variables.index(var) + 1)+'.png', dpi=500)
    plt.clf() 

os.chdir(code_folder)


#%%  Share of College Wage Premium due to ESHI over Time #%% 
# Parameter assumptions:
tau_param = 'tau_high'
alpha_c, alpha_n = 1, 1

# Parameter to be varied:
years = [1977,1987] + list(range(1996, 2019))

#Output path 
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Graphs/Visualize Results'

#Loop through years
df_byYear = pd.DataFrame(index=years, columns = ['College Wage Premium (H)', 'Chg. in College Wage Premium (P to H)', 'Share of College Wage Premium due to ESHI'])

for year in years:
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                tau=df_observed.loc[year, tau_param], 
                w1_c=df_observed.loc[year, 'wage_c'], 
                w1_n=df_observed.loc[year, 'wage_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                epop_ratio1=df_observed.loc[year, 'epop_ratio'],
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
    
    #Calculate variables of interest
    df_byYear.loc[year, 'College Wage Premium (H)'] = model.w1_c-model.w1_n
    df_byYear.loc[year, 'Chg. in College Wage Premium (P to H)'] = (model.w1_c-model.w1_n)-(model.w2_c-model.w2_n)
        
df_byYear['Share of College Wage Premium due to ESHI'] = df_byYear['Chg. in College Wage Premium (P to H)']/df_byYear['College Wage Premium (H)']


for year in [1977,1987,1997,2007]:
    chg_college_wage_premium = df_byYear.loc[2017, 'College Wage Premium (H)'] - df_byYear.loc[year, 'College Wage Premium (H)']
    chg_ESHI_contrib = df_byYear.loc[2017, 'Chg. in College Wage Premium (P to H)'] - df_byYear.loc[year, 'Chg. in College Wage Premium (P to H)'] 
    share_ESHI = chg_ESHI_contrib/chg_college_wage_premium
    
    print(f'Year {year}:')
    print(f'The college wage premium increased by ${chg_college_wage_premium:,.0f} from {year} to 2017 and ESHI accounts for ${chg_ESHI_contrib:,.0f} of this change or {share_ESHI:,.2%}')
    print('')

plt.plot(df_byYear['College Wage Premium (H)'])
plt.suptitle('College Wage Premium', y=1.03, fontsize=18)
plt.title(r'$(w^H_C - w^H_N)$', fontsize=10)

plt.plot(df_byYear['Chg. in College Wage Premium (P to H)'])
plt.suptitle('Contribution of ESHI to the College Wage Premium', y=1.03, fontsize=18)
plt.title(r'$\left[(w^H_C - w^H_N) - (w^P_C - w^P_N)\right]$', fontsize=10)

