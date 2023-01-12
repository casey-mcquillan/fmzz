#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:44:37 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
from scipy.optimize import fsolve


#%%  Define Class #%%
class fmzz_calibration_model_CCF:
    def __init__(self, alpha_c, alpha_n, rho, tau, tau_CCF,
                     elasticities,
                     w_c, w_n, P_c, P_n,
                     share_workers_c, share_pop_c, pop_count):
        
        # Store inputs as attributes of object
        self.alpha_c = alpha_c
        self.alpha_n = alpha_n
        self.rho = rho
        self.tau = tau
        self.tau_CCF = tau_CCF
        self.elasticities = elasticities
        
        self.w_c = w_c
        self.w_n = w_n
        
        self.P_c = P_c
        self.P_n = P_n
        
        self.share_workers_c = share_workers_c
        self.share_pop_c = share_pop_c
        self.pop_count = pop_count
        
        # Save variables implicitly defined by inputs
        self.share_workers_n = 1-share_workers_c
        self.share_pop_n = 1-share_pop_c
    
    ### Calibrate the Model ###
    def calibrate(self):
        # Define variables based on attributes of object
        alpha_c = self.alpha_c
        alpha_n = self.alpha_n
        rho = self.rho
        tau = self.tau
        tau_CCF = self.tau_CCF
        elasticities = self.elasticities
        
        w_c = self.w_c
        w_n = self.w_n
        
        P_c = self.P_c
        P_n = self.P_n
        
        share_workers_c = self.share_workers_c
        share_workers_n = self.share_workers_n
        share_pop_c = self.share_pop_c
        share_pop_n = self.share_pop_n
        pop_count = self.pop_count
        
        ### Solve for General Parameters ###
        # Solve for Labor Supply in Head Tax Eq
        L_c = P_c * share_pop_c
        L_n = P_n * share_pop_n
        # Solve for lambda parameter:
        x = ((w_n+tau)/(w_c+tau))*(L_n/L_c)**(1-rho)
        lambda_c = ((w_c+tau)*L_c**(1-rho)*(x*L_n**rho+L_c**rho)**(1-1/rho))**rho                 
        lambda_n = x*lambda_c
        # Solve for MPL:
        MPL_c = lambda_c*L_c**(rho-1)*(lambda_n*L_n**rho+lambda_c*L_c**rho)**(1/rho-1)
        MPL_n = lambda_n*L_n**(rho-1)*(lambda_n*L_n**rho+lambda_c*L_c**rho)**(1/rho-1)
        # Solve for Value in Head Tax Eq
        V_c = w_c + alpha_c * tau
        V_n = w_n + alpha_n * tau   
        # Solve for kappa parameters
        if elasticities=='implied':
            ##Solve for common kappa parameters 
            kappa_dist = (V_c - V_n)/(P_c - P_n)
            kappa_lb = V_c - P_c*kappa_dist
            kappa_ub = kappa_lb + kappa_dist
            # College
            kappa_lb_c = kappa_lb
            kappa_ub_c = kappa_ub
            kappa_dist_c = kappa_dist
            # Non-college
            kappa_lb_n = kappa_lb
            kappa_ub_n = kappa_ub
            kappa_dist_n = kappa_dist
            ## Then we can solve for elasticties
            elasticity_c = kappa_dist_c**(-1) * (w_c / P_c)
            elasticity_n = kappa_dist_n**(-1) * (w_n / P_n)
            
        else:
            ## Elasticities are given
            elasticity_c, elasticity_n = elasticities
            ## We solve for kappa parameters
            # College
            kappa_lb_c = w_c+tau-(w_c/elasticity_c)
            kappa_ub_c = (V_c-kappa_lb_c)/P_c + kappa_lb_c
            kappa_dist_c = kappa_ub_c-kappa_lb_c
            # Non-college
            kappa_lb_n = w_n+tau-(w_n/elasticity_n)
            kappa_ub_n = (V_n-kappa_lb_n)/P_n + kappa_lb_n
            kappa_dist_n = kappa_ub_n-kappa_lb_n
        
        # Solve for epop ratio in Head Tax Eq
        epop_ratio = (P_c*share_pop_c + P_n*share_pop_n)
        # Solve for average productivity in Head Tax Eq
        avg_MPL = share_workers_c * MPL_c + share_workers_n * MPL_n
        # Solve for wage bill share
        share_wage_bill_c = (L_c * w_c) / (L_c * w_c + L_n * w_n)
        share_wage_bill_n = (L_n * w_n) / (L_c * w_c + L_n * w_n)
        # Solve for employment levels
        employment = (L_c + L_n) * pop_count 
        employment_c = L_c * pop_count 
        employment_n = L_n * pop_count        
        
        ### Solve Cost Counterfactual ###
        #Set up nonlinear equation solver for wages and labor supply
        def equations(vars):
            w_n_CCF, w_c_CCF, L_n_CCF, L_c_CCF = vars
            eq1 = w_n_CCF + tau_CCF - lambda_n*L_n_CCF**(rho-1) \
                *(lambda_n*L_n_CCF**(rho)+lambda_c*L_c_CCF**(rho))**(1/rho-1)
            eq2 = w_c_CCF + tau_CCF - lambda_c*L_c_CCF**(rho-1) \
                *(lambda_n*L_n_CCF**(rho)+lambda_c*L_c_CCF**(rho))**(1/rho-1)
            eq3 = L_n_CCF - share_pop_n*((w_n_CCF + alpha_n*tau_CCF - kappa_lb_n)/kappa_dist_n)
            eq4 = L_c_CCF - share_pop_c*((w_c_CCF + alpha_c*tau_CCF - kappa_lb_c)/kappa_dist_c)
            return [eq1, eq2, eq3, eq4]
        
        #Let initial guess be based on Head Tax Eq   
        w_n_CCF_guess = w_n + tau
        w_c_CCF_guess = w_c + tau
        L_n_CCF_guess = share_pop_n*((w_n_CCF_guess+alpha_n*tau_CCF-kappa_lb_n)/kappa_dist_n)
        L_c_CCF_guess = share_pop_c*((w_c_CCF_guess+alpha_c*tau_CCF-kappa_lb_c)/kappa_dist_c)
        w_n_CCF, w_c_CCF, L_n_CCF, L_c_CCF =  fsolve(equations, (w_n_CCF_guess, w_c_CCF_guess,
                                                     L_n_CCF_guess, L_c_CCF_guess))
        
        #Solve for value of employment
        V_c_CCF = w_c_CCF + alpha_c*tau_CCF
        V_n_CCF = w_n_CCF + alpha_n*tau_CCF
        # Solve for Prob of working in No ESHI Eq
        P_c_CCF = (V_c_CCF - kappa_lb_c) / kappa_dist_c
        P_n_CCF = (V_n_CCF - kappa_lb_n) / kappa_dist_n
        # Solve for share of workers of each type in No ESHI Eq
        share_workers_c_CCF = L_c_CCF / (L_c_CCF + L_n_CCF)
        share_workers_n_CCF =  L_n_CCF / (L_c_CCF + L_n_CCF)
        # Solve for MPL in No ESHI Eq
        MPL_c_CCF = lambda_c*L_c_CCF**(rho-1)*(lambda_n*L_n_CCF**rho+lambda_c*L_c_CCF**rho)**(1/rho-1)
        MPL_n_CCF = lambda_n*L_n_CCF**(rho-1)*(lambda_n*L_n_CCF**rho+lambda_c*L_c_CCF**rho)**(1/rho-1)
        avg_MPL_CCF = share_workers_c_CCF * MPL_c_CCF + share_workers_n_CCF * MPL_n_CCF
        # Solve for e-pop ratio in No ESHI Eq
        epop_ratio_CCF = L_c_CCF + L_n_CCF
        # Solve for wage bill share
        share_wage_bill_c_CCF = (L_c_CCF * w_c_CCF) / (L_c_CCF * w_c_CCF + L_n_CCF * w_n_CCF)
        share_wage_bill_n_CCF = (L_n_CCF * w_n_CCF) / (L_c_CCF * w_c_CCF + L_n_CCF * w_n_CCF)
        # Solve for employment levels
        employment_CCF = (L_c_CCF + L_n_CCF) * pop_count 
        employment_c_CCF = L_c_CCF * pop_count 
        employment_n_CCF = L_n_CCF * pop_count
        
        ### Store variables as attributes of object ###
        general_params = ['pop_count']
        for var in general_params:
            exec("self."+var+"="+var)
            
        general_params_w_type = ['alpha','lambda', 'share_pop', 'elasticity', \
                                 'kappa_dist', 'kappa_lb', 'kappa_ub']
        for var in general_params_w_type:
            for _type in ['_c','_n']:        
                    exec("self."+var+_type+'='+var+_type)
        
        eq_values_w_type = ['w', 'P', 'L', 'MPL', 'share_workers', 'share_wage_bill', 'employment']
        for var in eq_values_w_type:
            for eq in ['', '_CCF']:
                for _type in ['_c','_n']:        
                    exec("self."+var+_type+eq+'='+var+_type+eq)
        
        eq_values_wo_type = ['avg_MPL', 'epop_ratio', 'employment']
        for var in eq_values_wo_type:
            for eq in ['', '_CCF']:
                exec("self."+var+eq+'='+var+eq)