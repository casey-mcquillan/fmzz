#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 12:24:00 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
from scipy.optimize import fsolve

### Set working directory
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
os.chdir(code_folder)

#%%  Define Class #%%
class calibration_model_bySex:
    def __init__(self, alpha_diff, rho, tau, 
                     elasticity_c, elasticity_n,
                     w1_c_m, w1_n_m, w1_c_f, w1_n_f, 
                     P1_c_m, P1_n_m, P1_c_f, P1_n_f,
                     share_workers1_c, share_pop_c,
                     share_workers1_c_m, share_pop_c_m,
                     share_workers1_n_m, share_pop_n_m,
                     pop_count):
        
        # Store inputs as attributes of object
        self.alpha_diff = alpha_diff
        self.rho = rho
        self.tau = tau
        self.elasticity_c = elasticity_c
        self.elasticity_n = elasticity_n
        
        #Wages
        self.w1_c_m = w1_c_m
        self.w1_n_m = w1_n_m
        self.w1_c_f = w1_c_f
        self.w1_n_f = w1_n_f
        
        #Employment Rate
        self.P1_c_m = P1_c_m
        self.P1_n_m = P1_n_m
        self.P1_c_f = P1_c_f
        self.P1_n_f = P1_n_f
        
        #Shares
        self.share_workers1_c = share_workers1_c
        self.share_workers1_c_m = share_workers1_c_m
        self.share_workers1_n_m = share_workers1_n_m
        self.share_pop_c = share_pop_c
        self.share_pop_c_m = share_pop_c_m
        self.share_pop_n_m = share_pop_n_m
        self.pop_count = pop_count
        
        # Save variables implicitly defined by inputs
        #Shares of workers
        self.share_workers1_c_f = share_workers1_c - share_workers1_c_m
        self.share_workers1_n = 1-share_workers1_c
        self.share_workers1_n_f = self.share_workers1_n - share_workers1_n_m
        #Shares of population
        self.share_pop_c_f = share_pop_c - share_pop_c_m
        self.share_pop_n = 1-share_pop_c
        self.share_pop_n_f = self.share_pop_n - share_pop_n_m
        
    
    ### Calibrate the Model ###
    def calibrate(self):
        # Define variables based on attributes of object
        alpha_diff = self.alpha_diff
        rho = self.rho
        tau = self.tau
        elasticity_c = self.elasticity_c
        elasticity_n = self.elasticity_n
        
        #Wages
        w1_c_m = self.w1_c_m
        w1_n_m = self.w1_n_m
        w1_c_f = self.w1_c_f
        w1_n_f = self.w1_n_f
        
        #Employment Rate
        P1_c_m = self.P1_c_m
        P1_n_m = self.P1_n_m
        P1_c_f = self.P1_c_f
        P1_n_f = self.P1_n_f
        
        #Shares
        share_workers1_c_m = self.share_workers1_c_m
        share_workers1_c_f = self.share_workers1_c_f
        share_workers1_n_m = self.share_workers1_n_m
        share_workers1_n_f = self.share_workers1_n_f
        share_pop_c_m = self.share_pop_c_m
        share_pop_c_f = self.share_pop_c_f
        share_pop_n_m = self.share_pop_n_m
        share_pop_n_f = self.share_pop_n_f
        pop_count = self.pop_count
        
        ### Head Tax Equilibrium & General Parameters ###
        # solve for xi parameter:
        X_c_m = 1
        X_n_m = 1
        X_c_f = (w1_c_f + tau) / (w1_c_m + tau)
        X_n_f = (w1_n_f + tau) / (w1_n_m + tau) 
        # Solve for Labor Supply in Head Tax Eq
        L1_c_m = P1_c_m * share_pop_c_m
        L1_n_m = P1_n_m * share_pop_n_m
        L1_c_f = P1_c_f * share_pop_c_f
        L1_n_f = P1_n_f * share_pop_n_f
        L1_c = X_c_m * L1_c_m + X_c_f * L1_c_f 
        L1_n = X_n_m * L1_n_m + X_n_f * L1_n_f 

        # Solve for lambda parameter:
        coef = ((w1_n_m+tau)/X_n_m) * ((w1_c_m+tau)/X_c_m)**(-1) * (L1_n/L1_c)**(1-rho)
        lambda_c = ( ((w1_c_m+tau)/X_c_m) * L1_c**(1-rho) * (coef*L1_n**rho+L1_c**rho)**(1-1/rho) )**rho                 
        lambda_n = coef*lambda_c
        
        # Solve for kappa parameters
        if elasticity_c==elasticity_c=='common':
            kappa_dist_m = (w1_c_m - w1_n_m + alpha_diff*tau)/(P1_c_m - P1_n_m)
            kappa_dist_f = (w1_c_f - w1_n_f + alpha_diff*tau)/(P1_c_f - P1_n_f)
            
            kappa_dist_c_m = kappa_dist_m
            kappa_dist_n_m = kappa_dist_m
            kappa_dist_c_f = kappa_dist_f
            kappa_dist_n_f = kappa_dist_f
        
            #elasticity_c = (w1_c)/(w1_c+tau-kappa_lb_c)
            #elasticity_n = (w1_n)/(w1_n+tau-kappa_lb_n)
            
        # else:
        #     Calulcate kappa_dist_g_s
    
        # Solve for MPL:
        MPL1_c_m = X_c_m*lambda_c*L1_c**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)
        MPL1_n_m = X_n_m*lambda_n*L1_n**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)
        MPL1_c_f = X_c_f*lambda_c*L1_c**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)
        MPL1_n_f = X_n_f*lambda_n*L1_n**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)        
        
        # Solve for average productivity in Head Tax Eq
        avg_MPL1 = share_workers1_c_m * MPL1_c_m + share_workers1_n_m * MPL1_n_m \
                    + share_workers1_c_f * MPL1_c_f + share_workers1_n_f * MPL1_n_f
                    
        # Solve for wage bill share
        share_wage_bill1_c_m = (L1_c_m * w1_c_m) / \
                                (L1_c_m * w1_c_m + L1_n_m * w1_n_m +\
                                 L1_c_f * w1_c_f + L1_n_f * w1_n_f)
        share_wage_bill1_n_m = (L1_n_m * w1_n_m) / \
                                (L1_c_m * w1_c_m + L1_n_m * w1_n_m +\
                                 L1_c_f * w1_c_f + L1_n_f * w1_n_f)
        share_wage_bill1_c_f = (L1_c_f * w1_c_f) / \
                                (L1_c_m * w1_c_m + L1_n_m * w1_n_m +\
                                 L1_c_f * w1_c_f + L1_n_f * w1_n_f)
        share_wage_bill1_n_f = (L1_n_f * w1_n_f) / \
                                (L1_c_m * w1_c_m + L1_n_m * w1_n_m +\
                                 L1_c_f * w1_c_f + L1_n_f * w1_n_f)
        # Solve for employment levels
        employment1_c_m = L1_c_m * pop_count 
        employment1_n_m = L1_n_m * pop_count
        employment1_c_f = L1_c_f * pop_count 
        employment1_n_f = L1_n_f * pop_count

    # Solve for epop ratio in Head Tax Eq
        epop_ratio1 = (P1_c_m*share_pop_c_m + P1_n_m*share_pop_n_m \
                       + P1_c_f*share_pop_c_f + P1_n_f*share_pop_n_f)
            
        ### Payroll Tax Equilibrium ###
        ## Solve for Payroll Tax rate
        #Set up nonlinear equation solver 
        def equations(vars):
            w2_n_m, w2_c_m, w2_n_f, w2_c_f, \
                L2_n_m, L2_c_m, L2_n_f, L2_c_f,\
                t = vars
            #Aggregate Labor    
            L2_c = X_c_m * L2_c_m + X_c_f * L2_c_f 
            L2_n = X_n_m * L2_n_m + X_n_f * L2_n_f 
        
            #Wages
            eq1_m = w2_n_m - X_n_m*(lambda_n*L2_n**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t) 
            eq1_f = w2_n_f - X_n_f*(lambda_n*L2_n**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t) 
            eq2_m = w2_c_m - X_c_m*(lambda_c*L2_c**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)
            eq2_f = w2_c_f - X_c_f*(lambda_c*L2_c**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)
            
            #Labor Supply
            eq3_m = L2_n_m - (L1_n_m + share_pop_n_m*(w2_n_m-w1_n_m)/(kappa_dist_m))
            eq3_f = L2_n_f - (L1_n_f + share_pop_n_f*(w2_n_f-w1_n_f)/(kappa_dist_f))
            eq4_m = L2_c_m - (L1_c_m + share_pop_c_m*(w2_c_m-w1_c_m)/(kappa_dist_m))
            eq4_f = L2_c_f - (L1_c_f + share_pop_c_f*(w2_c_f-w1_c_f)/(kappa_dist_f))
            
            #Balanced budget
            w_tilde = (L2_c_m * w2_c_m + L2_n_m * w2_n_m \
                       + L2_c_f * w2_c_f + L2_n_f * w2_n_f)
            eq5 = t - (tau*(L2_c_m+L2_n_m+L2_c_f+L2_n_f))/w_tilde
            
            return [eq1_m,eq1_f, eq2_m,eq2_f, eq3_m,eq3_f, eq4_m,eq4_f, eq5]
        
        #Let initial guess be based on Head Tax Eq
        t_guess = tau /(avg_MPL1 - tau)        
        w2_n_m_guess = MPL1_n_m/(1+t_guess)
        w2_c_m_guess = MPL1_c_m/(1+t_guess)
        w2_n_f_guess = MPL1_n_f/(1+t_guess)
        w2_c_f_guess = MPL1_c_f/(1+t_guess)
        L2_n_m_guess = L1_n_m + share_pop_n_m*(w2_n_m_guess-w1_n_m)/(kappa_dist_m)
        L2_c_m_guess = L1_c_m + share_pop_c_m*(w2_c_m_guess-w1_c_m)/(kappa_dist_m)
        L2_n_f_guess = L1_n_f + share_pop_n_f*(w2_n_f_guess-w1_n_f)/(kappa_dist_f)
        L2_c_f_guess = L1_c_f + share_pop_c_f*(w2_c_f_guess-w1_c_f)/(kappa_dist_f)
       
        #Solve 
        w2_n_m, w2_c_m,w2_n_f, w2_c_f,\
        L2_n_m, L2_c_m, L2_n_f, L2_c_f, \
                t =  fsolve(equations, (w2_n_m_guess, w2_c_m_guess,\
                                        w2_n_f_guess, w2_c_f_guess,\
                                        L2_n_m_guess, L2_c_m_guess,\
                                        L2_n_f_guess, L2_c_f_guess,\
                                        t_guess))
        
        # Solve for aggregate labor
        L2_c = X_c_m * L2_c_m + X_c_f * L2_c_f 
        L2_n = X_n_m * L2_n_m + X_n_f * L2_n_f 
        
        #Solve for employment rate
        P2_c_m = P1_c_m + (w2_c_m-w1_c_m) / kappa_dist_m
        P2_c_f = P1_c_f + (w2_c_f-w1_c_f) / kappa_dist_f
        P2_n_m = P1_n_m + (w2_n_m-w1_n_m) / kappa_dist_m
        P2_n_f = P1_n_f + (w2_n_f-w1_n_f) / kappa_dist_f
        
        #Solve for share of workers and avg. productivity
        share_workers2_c_m = L2_c_m / (L2_c_m + L2_n_m + L2_c_f + L2_n_f)
        share_workers2_n_m =  L2_n_m / (L2_c_m + L2_n_m + L2_c_f + L2_n_f)
        share_workers2_c_f = L2_c_f / (L2_c_m + L2_n_m + L2_c_f + L2_n_f)
        share_workers2_n_f =  L2_n_f / (L2_c_m + L2_n_m + L2_c_f + L2_n_f)
        
        # Solve for MPL in Payroll Tax Eq
        MPL2_c_m = X_c_m*lambda_c*L2_c**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        MPL2_n_m = X_n_m*lambda_n*L2_n**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        MPL2_c_f = X_c_f*lambda_c*L2_c**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        MPL2_n_f = X_n_f*lambda_n*L2_n**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        
        # Solve for average productivity in Head Tax Eq
        avg_MPL2 = share_workers2_c_m * MPL2_c_m + share_workers2_n_m * MPL2_n_m \
                    + share_workers2_c_f * MPL2_c_f + share_workers2_n_f * MPL2_n_f
            
        # Solve for wage bill share
        share_wage_bill2_c_m = (L2_c_m * w2_c_m) / \
                                (L2_c_m * w2_c_m + L2_n_m * w2_n_m +\
                                 L2_c_f * w2_c_f + L2_n_f * w2_n_f)
        share_wage_bill2_n_m = (L2_n_m * w2_n_m) / \
                                (L2_c_m * w2_c_m + L2_n_m * w2_n_m +\
                                 L2_c_f * w2_c_f + L2_n_f * w2_n_f)
        share_wage_bill2_c_f = (L2_c_f * w2_c_f) / \
                                (L2_c_m * w2_c_m + L2_n_m * w2_n_m +\
                                 L2_c_f * w2_c_f + L2_n_f * w2_n_f)
        share_wage_bill2_n_f = (L2_n_f * w2_n_f) / \
                                (L2_c_m * w2_c_m + L2_n_m * w2_n_m +\
                                 L2_c_f * w2_c_f + L2_n_f * w2_n_f)
        # Solve for employment levels
        employment2_c_m = L2_c_m * pop_count 
        employment2_n_m = L2_n_m * pop_count
        employment2_c_f = L2_c_f * pop_count 
        employment2_n_f = L2_n_f * pop_count
     
        # Solve for epop ratio in Head Tax Eq
        epop_ratio2 = (P2_c_m*share_pop_c_m + P2_n_m*share_pop_n_m \
                       + P2_c_f*share_pop_c_f + P2_n_f*share_pop_n_f)
        
                  
        ### Store variables as attributes of object ###
        general_params = ['tau', 'pop_count', 't']
        for var in general_params:
            exec("self."+var+"="+var)
            
        general_params_w_type = ['lambda']
        for var in general_params_w_type:
            for _type in ['_c','_n']:        
                    exec("self."+var+_type+'='+var+_type)
                    
        general_params_w_subtype = ['X', 'share_pop', 'kappa_dist']
        for var in general_params_w_subtype:
            for _type in ['_c','_n']:
                for _sex in ['_m','_f']:
                    exec("self."+var+_type+_sex+'='+var+_type+_sex)
        
        eq_values_w_type = ['w', 'P', 'L', 'MPL', 'share_workers', 'share_wage_bill', 'employment']
        for var in eq_values_w_type:
            for eq_num in ['1', '2']:
                for _type in ['_c','_n']:
                    for _sex in ['_m','_f']:        
                        exec("self."+var+eq_num+_type+_sex+'='+var+eq_num+_type+_sex)
        
        eq_values_wo_type = ['avg_MPL', 'epop_ratio']
        for var in eq_values_wo_type:
            for eq_num in ['1', '2']:
                exec("self."+var+eq_num+'='+var+eq_num)

#%%  Create Instance #%%

'''              
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_bySex.csv', index_col=0)

# Parameter assumptions:
alpha_diff=0
year = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]

#Define Model
model = calibration_model_bySex(alpha_diff=0,
                    rho=rho_baseline,
                    tau=df_observed.loc[year, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c_m=df_observed.loc[year, 'wage1_c_m'], 
                    w1_n_m=df_observed.loc[year, 'wage1_n_m'],
                    w1_c_f=df_observed.loc[year, 'wage1_c_f'], 
                    w1_n_f=df_observed.loc[year, 'wage1_n_f'],
                    P1_c_m=df_observed.loc[year, 'P1_c_m'], 
                    P1_n_m=df_observed.loc[year, 'P1_n_m'],
                    P1_c_f=df_observed.loc[year, 'P1_c_f'], 
                    P1_n_f=df_observed.loc[year, 'P1_n_f'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    share_workers1_c_m=df_observed.loc[year, 'share_workers1_c_m'],
                    share_pop_c_m=df_observed.loc[year, 'share_pop_c_m'],
                    share_workers1_n_m=df_observed.loc[year, 'share_workers1_n_m'],
                    share_pop_n_m=df_observed.loc[year, 'share_pop_n_m'],
                    pop_count=df_observed.loc[year, 'pop_count'])

#Make sure there are no NANs in model before calibration
# Remove elasticities if specified to be common
if model.elasticity_c == model.elasticity_n == 'common': 
    check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
else: check = vars(model).keys()
#And now check
if any(np.isnan([vars(model)[x] for x in check])):
    print("NAN value entered into calibration model for:")
    for var in check:
        if np.isnan(vars(model)[var])==True: print("    "+var)
    print("for year: " + str(year))

#Calibrate Model
model.calibrate()
'''