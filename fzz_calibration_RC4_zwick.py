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

### Set working directory
folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
os.chdir(folder)

#%%  Define Class #%%
class calibration_model_RC4:
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
        L0_n_guess = share_pop_n*((w0_n_guess+alpha_n*tau-kappa_lb_n)/kappa_dist_n)
        L0_c_guess = share_pop_c*((w0_c_guess+alpha_c*tau-kappa_lb_c)/kappa_dist_c)
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


    ### Generate Tables in Tex ###
    def generate_table(self, file_name, year, table_type, table_label, location, subtitle=''):
        
        ## Generate Summary Table
        if table_type=="equilibrium summary":
        
            ## Generate Strings that will be written into .tex file as a list
            header = [f'\ctable[caption={{Equilibrium Summary for {year}', subtitle, '},', '\n',
            f'    label={table_label}, pos=h!]', '\n',
            '{rcccrccc}{^{*}&{This represents an observed value.}}', '\n',
            '{\FL &&&&& \multicolumn{3}{c}{Equilibrium Values}  \\\\', '\n',
            '\cmidrule{6-8}', '\n',
            '   \multicolumn{2}{c}{General Parameters} &&&&  No ESHI  &  Head Tax  & Payroll Tax  \\\\', '\n',
            '\cmidrule{1-8}', '\n']
    
            table_values = [f'$\lambda_C$ & {self.lambda_c:,.3f} &&&', '\n',
                f'$w_C$ & {self.w0_c:,.0f} & {self.w1_c:,.0f}\\tmark[*] & {self.w2_c:,.0f} \\\\', '\n',
                f'$\lambda_N$ & {self.lambda_n:,.3f} &&&', '\n',
                f'$w_N$ & {self.w0_n:,.0f} & {self.w1_n:,.0f}\\tmark[*] & {self.w2_n:,.0f} \\\\', '\n',
                f'$\\tau$ & {self.tau:,.0f}\\tmark[*] &&&', '\n',
                f'$w_C/w_N$ & {self.w0_c/self.w0_n:,.3f} & {self.w1_c/self.w1_n:,.3f} & {self.w2_c/self.w2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'$N_C$ & {self.share_pop_c:,.3f}\\tmark[*] &&&', '\n',
                f'$P_C$ & {self.P0_c:,.3f} & {self.P1_c:,.3f}\\tmark[*] & {self.P2_c:,.3f} \\\\', '\n',
                f'$N_N$ & {self.share_pop_n:,.3f}  &&&', '\n',
                f'$P_N$ & {self.P0_n:,.3f} & {self.P1_n:,.3f}\\tmark[*] & {self.P2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'$\\overline{{\kappa}}_C$ & {self.kappa_ub_c:,.0f} &&&', '\n',
                f'$L_C$ & {self.L0_c:,.3f} & {self.L1_c:,.3f} & {self.L2_c:,.3f} \\\\', '\n',
                f'$\\underline{{\kappa}}_C$ &  {self.kappa_lb_c:,.0f} &&&', '\n',
                f'$L_N$ & {self.L0_n:,.3f} & {self.L1_n:,.3f} & {self.L2_n:,.3f} \\\\', '\n',
                f'$(\\overline{{\kappa}}_C - \\underline{{\kappa}}_C)$ & {self.kappa_dist_c:,.0f} &&&', '\n',
                f'$L_C/L_N$ & {self.L0_c/self.L0_n:,.3f} & {self.L1_c/self.L1_n:,.3f} & {self.L2_c/self.L2_n:,.3f}  \\\\', '\n',
                '\\\\\n',
                f'$\\overline{{\kappa}}_N$ & {self.kappa_ub_n:,.0f} &&&', '\n',
                'Share of Workforce \\\\', '\n',
                f'$\\underline{{\kappa}}_N$ &  {self.kappa_lb_n:,.0f} &&&', '\n',
                f'\\indent \\small College & {self.share_workers0_c:,.3f} & {self.share_workers1_c:,.3f}\\tmark[*] & {self.share_workers2_c:,.3f} \\\\', '\n',
                f'$(\\overline{{\kappa}}_N - \\underline{{\kappa}}_N)$ & {self.kappa_dist_n:,.0f} &&&', '\n',
                f'\\indent \\small Non-college & {self.share_workers0_n:,.3f} & {self.share_workers1_n:,.3f} & {self.share_workers2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'Payroll Tax & {self.t * 100:,.2f}\\% &&&', '\n',
                f'E:P Ratio & {self.epop_ratio0:,.3f} & {self.epop_ratio1:,.3f} & {self.epop_ratio2:,.3f} \\\\', '\n', 
                '\\\\\n',
                f'Pop. Count & {self.pop_count:,.0f}\\tmark[*] &&&', '\n',
                f'$MPL_C$ & {self.MPL0_c:,.0f} & {self.MPL1_c:,.0f} & {self.MPL2_c:,.0f} \\\\', '\n',
                f'& &&& $MPL_N$ & {self.MPL0_n:,.0f} & {self.MPL1_n:,.0f} & {self.MPL2_n:,.0f}  \\\\', '\n',
                '\\\\\n',
                '& &&& Share of Workforce \\\\', '\n',
                f'& &&& \\indent \\small College & {self.share_workers0_c:,.3f} & {self.share_workers1_c:,.3f}\\tmark[*] & {self.share_workers2_c:,.3f} \\\\', '\n',
                f'& &&& \\indent \\small Non-college & {self.share_workers0_n:,.3f} & {self.share_workers1_n:,.3f} & {self.share_workers2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                '& &&& Share of Wage Bill \\\\', '\n',
                f'& &&& \\indent \\small College & {self.share_wage_bill0_c:,.3f} & {self.share_wage_bill1_c:,.3f} & {self.share_wage_bill2_c:,.3f} \\\\', '\n',
                f'& &&& \\indent \\small Non-college & {self.share_wage_bill0_n:,.3f} & {self.share_wage_bill1_n:,.3f} & {self.share_wage_bill2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'& &&& Employment (Thous.) & {self.employment0/1000:,.0f} & {self.employment1/1000:,.0f} & {self.employment2/1000:,.0f} \\\\', '\n',
                f'& &&& \\indent \\small College & {self.employment0_c/1000:,.0f} & {self.employment1_c/1000:,.0f} & {self.employment2_c/1000:,.0f} \\\\', '\n',
                f'& &&& \\indent \\small Non-college & {self.employment0_n/1000:,.0f} & {self.employment1_n/1000:,.0f} & {self.employment2_n/1000:,.0f} \\\\', '\n',
                '\\\\\n',
                f'& &&& Average Welfare & {self.welfare0:,.0f} & {self.welfare1:,.0f} & {self.welfare2:,.0f} \\\\', '\n',
                f'& &&& \\indent \\small College & {self.welfare0_c:,.0f} & {self.welfare1_c:,.0f} & {self.welfare2_c:,.0f} \\\\', '\n',
                f'& &&& \\indent \\small Non-college & {self.welfare0_n:,.0f} & {self.welfare1_n:,.0f} & {self.welfare2_n:,.0f} \\\\', '\n',
                f'& &&& \\indent \\small Difference & {self.welfare0_c-self.welfare0_n:,.0f} ',
                    f'& {self.welfare1_c-self.welfare1_n:,.0f} ',
                    f'& {self.welfare2_c-self.welfare2_n:,.0f} \\\\', '\n']

            closer = ['\\bottomrule}']
    
            #Create, write, and close file
            cwd = os.getcwd()
            os.chdir(location)
            file = open(file_name+".tex","w")
            file.writelines(header) 
            file.writelines(table_values)   
            file.writelines(closer)   
            file.close()
            
            #Return to previous directory
            os.chdir(cwd)
            
            
        ## Generate Comparison Table
        if table_type=="equilibrium comparison":

            header = [f'\ctable[caption={{Equilibrium Comparison for {year}', subtitle, '},', '\n',
                        f'    label={table_label}, pos=h!]', '\n',
                        '{lc}{}{\\FL', '\n',
                        '   & \\small (Head Tax $\\Rightarrow$ Payroll Tax)  \\\\', '\n',
                        '\cmidrule{1-2}', '\n']

            table_values = ['\\underline{Wages:}', ' \\\\\n',
                f'\\ \\ $\\Delta(w_C)$'
                    f' & {self.w2_c-self.w1_c:,.0f}',
                    ' \\\\\n',
                f'\\ \\ $\\Delta(w_N)$',
                    f' & {self.w2_n-self.w1_n:,.0f}',
                    ' \\\\\n',
                f'\\ \\ $\\Delta(w_C - w_N)$'
                    f' & {(self.w2_c-self.w2_n)-(self.w1_c-self.w1_n):,.0f}',
                    ' \\\\\n',
                f'\\ \\ $\\%\\Delta(w_C - w_N)$'
                    f' & {100*((self.w2_c-self.w2_n)-(self.w1_c-self.w1_n))/(self.w1_c-self.w1_n):,.2f}\\%',
                    ' \\\\\n',
                f'\\ \\ $\\%\\Delta(w_C/w_N - 1)$'
                    f' & {100*((self.w2_c/self.w2_n)-(self.w1_c/self.w1_n))/(self.w1_c/self.w1_n - 1):,.2f}\\%',
                    ' \\\\\n',
                    '\\\\\n',
            '\\underline{Labor Supply:}', ' \\\\\n',
                f'\\ \\ $\\%\\Delta(L_C+L_N)$'
                    f' & {100*((self.L2_c+self.L2_n)-(self.L1_c+self.L1_n))/(self.L1_c+self.L1_n):,.2f}\\%',
                    ' \\\\\n'
                f'\\ \\ $\\%\\Delta(L_C)$'
                    f' & {100*(self.L2_c-self.L1_c)/self.L1_c:,.2f}\\%',
                    ' \\\\\n'
                f'\\ \\ $\\%\\Delta(L_N)$'
                    f' & {100*(self.L2_n-self.L1_n)/self.L1_n:,.2f}\\%',
                    ' \\\\\n',
                    '\\\\\n',
            '\\underline{Employment:}', ' \\\\\n',
            '$\\Delta$(\\small College Share):', 
                    f' & {100*(((self.L2_c)/(self.L2_c+self.L2_n))-((self.L1_c)/(self.L1_c+self.L1_n))):,.2f} pp',
                    ' \\\\\n',
            '$\\Delta$(\\small Total Employment):',
                    f' & {(self.employment2_c+self.employment2_n)-(self.employment1_c+self.employment1_n):,.0f}',
                    ' \\\\\n',
                '\\ \\ \\small College',
                    f' & {self.employment2_c-self.employment1_c:,.0f}',
                    ' \\\\\n',
                '\\ \\ \\small Non-College',
                    f' & {self.employment2_n-self.employment1_n:,.0f}',
                    ' \\\\\n',
                    '\\\\\n',
            '\\underline{Wage Bill:}', ' \\\\\n',
                '\\small $\\Delta($College Share$)$',
                    f' & {100*(((self.L2_c*self.w2_c)/(self.L2_c*self.w2_c + self.L2_n*self.w2_n))-((self.L1_c*self.w1_c)/(self.L1_c*self.w1_c + self.L1_n*self.w1_n))):,.2f} pp',
                    ' \\\\\n']

            closer = ['\\bottomrule}']

            #Create, write, and close file
            cwd = os.getcwd()
            os.chdir(location)
            file = open(file_name+".tex","w")
            file.writelines(header)
            file.writelines(table_values)
            file.writelines(closer)
            file.close()
            
            #Return to previous directory
            os.chdir(cwd)


#%%  Create Instance #%%
            
'''
# Importing Data
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year = 2019
e_c = 'common'
e_n = 'common'

#Define and calibrate model
model = calibration_model_RC4(alpha_c, alpha_n,
            rho=1/3,
            elasticity_c=e_c, elasticity_n=e_n,
            tau=df_observed.loc[year, 'tau_high'], 
            w1_c=df_observed.loc[year, 'wage1_c'], 
            w1_n=df_observed.loc[year, 'wage1_n'],
            P1_c=df_observed.loc[year, 'P1_c'], 
            P1_n=df_observed.loc[year, 'P1_n'],
            share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
            share_pop_c=df_observed.loc[year, 'share_pop_c'],
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

#Output LaTeX Tables
output_path = '/Users/caseymcquillan/Desktop/'
model.generate_table(file_name='SummaryTable'+str(year)+"_RC4", year=year, 
                     table_type="equilibrium summary",
                     table_label="SummaryTable"+str(year)+"baseline", 
                     location=output_path, subtitle=" with CES Labor Demand")

model.generate_table(file_name='EqComparison'+str(year)+"_RC4", year=year, 
                 table_type="equilibrium comparison", 
                 table_label="EqComparison"+str(year)+"baseline", 
                 location=output_path, subtitle=" with CES Labor Demand")

'''