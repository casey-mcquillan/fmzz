#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:01:21 2021

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
from scipy.optimize import fsolve


#%%  Define Class #%%
class fmzz_calibration_model:
    def __init__(self, alpha_diff, rho, tau, 
                     elasticities,
                     w1_c, w1_n, P1_c, P1_n,
                     share_workers1_c, share_pop_c, pop_count):
        
        # Store inputs as attributes of object
        self.alpha_diff = alpha_diff
        self.rho = rho
        self.tau = tau
        self.elasticities = elasticities
        
        self.w1_c = w1_c
        self.w1_n = w1_n
        
        self.P1_c = P1_c
        self.P1_n = P1_n
        
        self.share_workers1_c = share_workers1_c
        self.share_pop_c = share_pop_c
        self.pop_count = pop_count
        
        # Save variables implicitly defined by inputs
        self.share_workers1_n = 1-share_workers1_c
        self.share_pop_n = 1-share_pop_c
    
    ### Calibrate the Model ###
    def calibrate(self):
        # Define variables based on attributes of object
        alpha_diff = self.alpha_diff
        rho = self.rho
        tau = self.tau
        elasticities = self.elasticities
        
        w1_c = self.w1_c
        w1_n = self.w1_n
        
        P1_c = self.P1_c
        P1_n = self.P1_n
        
        share_workers1_c = self.share_workers1_c
        share_workers1_n = self.share_workers1_n
        share_pop_c = self.share_pop_c
        share_pop_n = self.share_pop_n
        pop_count = self.pop_count
        
        ### Head Tax Equilibrium & General Parameters ###
        # Solve for Labor Supply in Head Tax Eq
        L1_c = P1_c * share_pop_c
        L1_n = P1_n * share_pop_n
        # Solve for lambda parameter:
        x = ((w1_n+tau)/(w1_c+tau))*(L1_n/L1_c)**(1-rho)
        lambda_c = ((w1_c+tau)*L1_c**(1-rho)*(x*L1_n**rho+L1_c**rho)**(1-1/rho))**rho                 
        lambda_n = x*lambda_c
        # Solve for MPL:
        MPL1_c = lambda_c*L1_c**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)
        MPL1_n = lambda_n*L1_n**(rho-1)*(lambda_n*L1_n**rho+lambda_c*L1_c**rho)**(1/rho-1)
 
        # Solve for kappa parameters
        if elasticities=='implied':
            # We solve for kappa dist using this fact
            kappa_dist = ((w1_c - w1_n)+(alpha_diff*tau))/(P1_c - P1_n)            
            kappa_dist_c = kappa_dist
            kappa_dist_n = kappa_dist
            # Then we can solve for elasticties
            elasticity_c = kappa_dist_c**(-1) * (w1_c / P1_c)
            elasticity_n = kappa_dist_n**(-1) * (w1_n / P1_n)
            
        else:
            # Elasticities are given
            elasticity_c, elasticity_n = elasticities
            # We solve for kappa dist  
            kappa_dist_c = elasticity_c**(-1) * (w1_c / P1_c)
            kappa_dist_n = elasticity_n**(-1) * (w1_n / P1_n)

        # Solve for epop ratio in Head Tax Eq
        epop_ratio1 = (P1_c*share_pop_c + P1_n*share_pop_n)
        # Solve for average productivity in Head Tax Eq
        avg_MPL1 = share_workers1_c * MPL1_c + share_workers1_n * MPL1_n
        # Solve for wage bill share
        share_wage_bill1_c = (L1_c * w1_c) / (L1_c * w1_c + L1_n * w1_n)
        share_wage_bill1_n = (L1_n * w1_n) / (L1_c * w1_c + L1_n * w1_n)
        # Solve for employment levels
        employment1 = (L1_c + L1_n) * pop_count 
        employment1_c = L1_c * pop_count 
        employment1_n = L1_n * pop_count        
                
        ### Payroll Tax Equilibrium ###
        #Set up nonlinear equation solver fior wages, labor supply, and tax rate
        def equations(vars):
            w2_n, w2_c, L2_n, L2_c, t = vars
            eq1 = w2_n - (lambda_n*L2_n**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)              
            eq2 = w2_c - (lambda_c*L2_c**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)    
            eq3 = (L2_n - L1_n) - share_pop_n*(w2_n-w1_n)/kappa_dist_n
            eq4 = (L2_c - L1_c) - share_pop_c*(w2_c-w1_c)/kappa_dist_c
            MPL_tilde = (L2_n/(L2_n+L2_c))*(lambda_n*L2_n**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1)) \
                + (L2_c/(L2_n+L2_c))*(lambda_c*L2_c**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))
            eq5 = t - (tau/(MPL_tilde-tau))
            return [eq1, eq2, eq3, eq4, eq5]
        #Let initial guess be based on Head Tax Eq
        t_guess = tau /(avg_MPL1 - tau)        
        w2_n_guess = MPL1_n/(1+t_guess)
        w2_c_guess = MPL1_c/(1+t_guess)
        L2_n_guess = L1_n + share_pop_n*(w2_n_guess-w1_n)/kappa_dist_n
        L2_c_guess = L1_c + share_pop_c*(w2_c_guess-w1_c)/kappa_dist_c
        w2_n, w2_c, L2_n, L2_c, t =  fsolve(equations, (w2_n_guess, w2_c_guess,\
                                                        L2_n_guess, L2_c_guess,\
                                                        t_guess))

        #Solve for employment rate
        P2_c = L2_c / share_pop_c
        P2_n = L2_n / share_pop_n
        #Solve for share of workers and avg. productivity
        share_workers2_c = L2_c / (L2_c + L2_n)
        share_workers2_n =  L2_n / (L2_c + L2_n)
        # Solve for MPL in No ESHI Eq
        MPL2_c = lambda_c*L2_c**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        MPL2_n = lambda_n*L2_n**(rho-1)*(lambda_n*L2_n**rho+lambda_c*L2_c**rho)**(1/rho-1)
        avg_MPL2 = share_workers2_c * MPL2_c + share_workers2_n * MPL2_n
        # Solve for e-pop ratio in Payroll Tax Eq
        epop_ratio2 = L2_c + L2_n
        # Solve for wage bill share
        share_wage_bill2_c = (L2_c * w2_c) / (L2_c * w2_c + L2_n * w2_n)
        share_wage_bill2_n = (L2_n * w2_n) / (L2_c * w2_c + L2_n * w2_n)
        # Solve for employment levels
        employment2 = (L2_c + L2_n) * pop_count 
        employment2_c = L2_c * pop_count 
        employment2_n = L2_n * pop_count     
                  
        ### Store variables as attributes of object ###
        general_params = ['alpha_diff', 'tau', 'pop_count', 't']
        for var in general_params:
            exec("self."+var+"="+var)
            
        general_params_w_type = ['lambda', 'share_pop', 'elasticity','kappa_dist']
        for var in general_params_w_type:
            for _type in ['_c','_n']:        
                    exec("self."+var+_type+'='+var+_type)
        
        eq_values_w_type = ['w', 'P', 'L', 'MPL', 'share_workers', 'share_wage_bill', 'employment']
        for var in eq_values_w_type:
            for eq_num in ['1', '2']:
                for _type in ['_c','_n']:        
                    exec("self."+var+eq_num+_type+'='+var+eq_num+_type)
        
        eq_values_wo_type = ['avg_MPL', 'epop_ratio', 'employment']
        for var in eq_values_wo_type:
            for eq_num in ['1', '2']:
                exec("self."+var+eq_num+'='+var+eq_num)