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
    def __init__(self, alpha_c, alpha_n, rho, tau, 
                     elasticity_c, elasticity_n,
                     w1_c, w1_n, P1_c, P1_n,
                     share_workers1_c, share_pop_c, pop_count):
        
        # Store inputs as attributes of object
        self.alpha_c = alpha_c
        self.alpha_n = alpha_n
        self.rho = rho
        self.tau = tau
        self.elasticity_c = elasticity_c
        self.elasticity_n = elasticity_n
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
        alpha_c = self.alpha_c
        alpha_n = self.alpha_n
        rho = self.rho
        tau = self.tau
        elasticity_c = self.elasticity_c
        elasticity_n = self.elasticity_n
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
        # Solve for Value in Head Tax Eq
        V1_c = w1_c + alpha_c * tau
        V1_n = w1_n + alpha_n * tau   
        # Solve for kappa parameters
        if elasticity_c==elasticity_c=='common':
            kappa_dist = (V1_c - V1_n)/(P1_c - P1_n)
            kappa_lb = V1_c - P1_c*kappa_dist
            kappa_ub = kappa_lb + kappa_dist
            
            kappa_lb_c = kappa_lb
            kappa_ub_c = kappa_ub
            kappa_dist_c =kappa_dist
            kappa_lb_n = kappa_lb
            kappa_ub_n = kappa_ub
            kappa_dist_n = kappa_dist
            
            elasticity_c = (w1_c)/(w1_c+tau-kappa_lb_c)
            elasticity_n = (w1_n)/(w1_n+tau-kappa_lb_n)
            
        else:
            kappa_lb_c = w1_c+tau-(w1_c/elasticity_c)
            kappa_ub_c = (V1_c-kappa_lb_c)/P1_c + kappa_lb_c
            kappa_dist_c = kappa_ub_c-kappa_lb_c
            kappa_lb_n = w1_n+tau-(w1_n/elasticity_n)
            kappa_ub_n = (V1_n-kappa_lb_n)/P1_n + kappa_lb_n
            kappa_dist_n = kappa_ub_n-kappa_lb_n
        
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
        # solve for welfare
        welfare1_c = ((V1_c-kappa_lb_c)**2)/(2*kappa_dist_c)
        welfare1_n = ((V1_n-kappa_lb_n)**2)/(2*kappa_dist_n)
        welfare1 = share_pop_c*welfare1_c + share_pop_n*welfare1_n
        
        
        ### No ESHI Equilibrium ###
        #Set up nonlinear equation solver for wages and labor supply
        def equations(vars):
            w0_n, w0_c, L0_n, L0_c = vars
            eq1 = w0_n - lambda_n*L0_n**(rho-1) \
                *(lambda_n*L0_n**(rho)+lambda_c*L0_c**(rho))**(1/rho-1)
            eq2 = w0_c-lambda_c*L0_c**(rho-1) \
                *(lambda_n*L0_n**(rho)+lambda_c*L0_c**(rho))**(1/rho-1)
            eq3 = L0_n - share_pop_n*((w0_n-kappa_lb_n)/kappa_dist_n)
            eq4 = L0_c - share_pop_c*((w0_c-kappa_lb_c)/kappa_dist_c)
            return [eq1, eq2, eq3, eq4]
        #Let initial guess be based on Head Tax Eq   
        w0_n_guess = w1_n + tau
        w0_c_guess = w1_c + tau
        L0_n_guess = share_pop_n*((w0_n_guess-kappa_lb_n)/kappa_dist_n)
        L0_c_guess = share_pop_c*((w0_c_guess-kappa_lb_c)/kappa_dist_c)
        w0_n, w0_c, L0_n, L0_c =  fsolve(equations, (w0_n_guess, w0_c_guess,
                                                     L0_n_guess, L0_c_guess))
        #Solve for value of employment
        V0_c = w0_c
        V0_n = w0_n
        # Solve for Prob of working in No ESHI Eq
        P0_c = (V0_c - kappa_lb_c) / kappa_dist_c
        P0_n = (V0_n - kappa_lb_n) / kappa_dist_n
        # Solve for share of workers of each type in No ESHI Eq
        share_workers0_c = L0_c / (L0_c + L0_n)
        share_workers0_n =  L0_n / (L0_c + L0_n)
        # Solve for MPL in No ESHI Eq
        MPL0_c = lambda_c*L0_c**(rho-1)*(lambda_n*L0_n**rho+lambda_c*L0_c**rho)**(1/rho-1)
        MPL0_n = lambda_n*L0_n**(rho-1)*(lambda_n*L0_n**rho+lambda_c*L0_c**rho)**(1/rho-1)
        avg_MPL0 = share_workers0_c * MPL0_c + share_workers0_n * MPL0_n
        # Solve for e-pop ratio in No ESHI Eq
        epop_ratio0 = L0_c + L0_n
        # Solve for wage bill share
        share_wage_bill0_c = (L0_c * w0_c) / (L0_c * w0_c + L0_n * w0_n)
        share_wage_bill0_n = (L0_n * w0_n) / (L0_c * w0_c + L0_n * w0_n)
        # Solve for employment levels
        employment0 = (L0_c + L0_n) * pop_count 
        employment0_c = L0_c * pop_count 
        employment0_n = L0_n * pop_count
        # Solve for welfare
        welfare0_c = ((V0_c-kappa_lb_c)**2)/(2*kappa_dist_c)
        welfare0_n = ((V0_n-kappa_lb_n)**2)/(2*kappa_dist_n)
        welfare0 = share_pop_c*welfare0_c + share_pop_n*welfare0_n
        
        
        ### Payroll Tax Equilibrium ###
        #Solve for Payroll Tax rate
        #Set up nonlinear equation solver 
        def equations(vars):
            w2_n, w2_c, L2_n, L2_c, t = vars
            eq1 = w2_n - (lambda_n*L2_n**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)              
            eq2 = w2_c - (lambda_c*L2_c**(rho-1) \
                *(lambda_n*L2_n**(rho)+lambda_c*L2_c**(rho))**(1/rho-1))/(1+t)    
            eq3 = L2_n - share_pop_n*((w2_n+alpha_n*tau-kappa_lb_n)/(kappa_ub_n-kappa_lb_n))
            eq4 = L2_c - share_pop_c*((w2_c+alpha_c*tau-kappa_lb_c)/(kappa_ub_c-kappa_lb_c))
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
        L2_n_guess = share_pop_n*((w2_n_guess+alpha_n*tau-kappa_lb_n)/(kappa_ub_n-kappa_lb_n))
        L2_c_guess = share_pop_c*((w2_c_guess+alpha_c*tau-kappa_lb_c)/(kappa_ub_c-kappa_lb_c))
        w2_n, w2_c, L2_n, L2_c, t =  fsolve(equations, (w2_n_guess, w2_c_guess,\
                                                        L2_n_guess, L2_c_guess,\
                                                        t_guess))
        #Solve for value of employment
        V2_c = w2_c + alpha_c * tau
        V2_n = w2_n + alpha_n * tau
        #Solve for employment rate
        P2_c = (V2_c - kappa_lb_c) / kappa_dist_c
        P2_n = (V2_n - kappa_lb_n) / kappa_dist_n
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
        # Solve for welfare
        welfare2_c = ((V2_c-kappa_lb_c)**2)/(2*kappa_dist_c)
        welfare2_n = ((V2_n-kappa_lb_n)**2)/(2*kappa_dist_n)
        welfare2 = share_pop_c*welfare2_c + share_pop_n*welfare2_n
     
                  
        ### Store variables as attributes of object ###
        general_params = ['tau', 'pop_count', 't']
        for var in general_params:
            exec("self."+var+"="+var)
            
        general_params_w_type = ['alpha','lambda', 'share_pop', 'elasticity', \
                                 'kappa_dist', 'kappa_lb', 'kappa_ub']
        for var in general_params_w_type:
            for _type in ['_c','_n']:        
                    exec("self."+var+_type+'='+var+_type)
        
        eq_values_w_type = ['w', 'V', 'P', 'L', 'MPL', 'share_workers', 'share_wage_bill', 'employment', 'welfare']
        for var in eq_values_w_type:
            for eq_num in ['0', '1', '2']:
                for _type in ['_c','_n']:        
                    exec("self."+var+eq_num+_type+'='+var+eq_num+_type)
        
        eq_values_wo_type = ['avg_MPL', 'epop_ratio', 'employment', 'welfare']
        for var in eq_values_wo_type:
            for eq_num in ['0', '1', '2']:
                exec("self."+var+eq_num+'='+var+eq_num)