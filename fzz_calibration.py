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

### Set working directory
folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
os.chdir(folder)

#%%  Define Class #%%
class calibration_model:
    def __init__(self, alpha_c, alpha_n,
                         tau, w1_c, w1_n, 
                         share_workers1_c, share_pop_c, 
                         epop_ratio1, pop_count,
                         t_epsilon=1e-30):
        # Store inputs as attributes of object
        self.alpha_c = alpha_c
        self.alpha_n = alpha_n
        self.tau = tau
        self.w1_c = w1_c
        self.w1_n = w1_n
        self.share_workers1_c = share_workers1_c
        self.share_pop_c = share_pop_c
        self.epop_ratio1 = epop_ratio1
        self.pop_count = pop_count
        self.t_epsilon = t_epsilon
        # Save variables implicitly defined by inputs
        self.share_workers1_n = 1-share_workers1_c
        self.share_pop_n = 1-share_pop_c
    
    ### Calibrate the Model ###
    def calibrate(self):
        # Define variables based on attributes of object
        alpha_c = self.alpha_c
        alpha_n = self.alpha_n
        tau = self.tau
        w1_c = self.w1_c
        w1_n = self.w1_n
        share_workers1_c = self.share_workers1_c
        share_workers1_n = self.share_workers1_n
        share_pop_c = self.share_pop_c
        share_pop_n = self.share_pop_n
        epop_ratio1 = self.epop_ratio1
        pop_count = self.pop_count
        t_epsilon = self.t_epsilon
        
        ## Head Tax Equilibrium & General Parameters ##
        # Solve for productivity
        A_c = w1_c + tau
        A_n = w1_n + tau
        # Solve for Value in Head Tax Eq
        V1_c = w1_c + alpha_c * tau
        V1_n = w1_n + alpha_n * tau
        # Solve for Prob of working in Head Tax Eq
        P1_c = epop_ratio1 * (share_workers1_c/share_pop_c)
        P1_n = epop_ratio1 * (share_workers1_n/share_pop_n)
        # Solve for Labor Supply in Head Tax Eq
        L1_c = P1_c * share_pop_c
        L1_n = P1_n * share_pop_n
        # Solve for kappa parameters
        kappa_dist = (V1_c - V1_n)/(P1_c - P1_n)
        kappa_lb = V1_c - P1_c*kappa_dist
        kappa_ub = kappa_lb + kappa_dist
        # Solve for average productivity in Head Tax Eq
        avg_prod1 = share_workers1_c * A_c + share_workers1_n * A_n
        # Solve for wage bill share
        share_wage_bill1_c = (L1_c * w1_c) / (L1_c * w1_c + L1_n * w1_n)
        share_wage_bill1_n = (L1_n * w1_n) / (L1_c * w1_c + L1_n * w1_n)
        # Solve for employment levels
        employment1 = (L1_c + L1_n) * pop_count 
        employment1_c = L1_c * pop_count 
        employment1_n = L1_n * pop_count
        
        ## No ESHI Equilibrium ##
        # Solve for w in No ESHI Eq
        w0_c = A_c
        w0_n = A_n
        # Solve for Value in No ESHI Eq
        V0_c = w0_c
        V0_n = w0_n
        # Solve for Prob of working in No ESHI Eq
        P0_c = (V0_c - kappa_lb) / kappa_dist
        P0_n = (V0_n - kappa_lb) / kappa_dist
        # Solve for Labor Supply in No ESHI Eq
        L0_c = P0_c * share_pop_c
        L0_n = P0_n * share_pop_n
        # Solve for share of workers of each type in No ESHI Eq
        share_workers0_c = L0_c / (L0_c + L0_n)
        share_workers0_n =  L0_n / (L0_c + L0_n)
        # Solve for average productivity in No ESHI Eq
        avg_prod0 = share_workers0_c * A_c + share_workers0_n * A_n
        # Solve for e-pop ratio in No ESHI Eq
        epop_ratio0 = L0_c + L0_n
        # Solve for wage bill share
        share_wage_bill0_c = (L0_c * w0_c) / (L0_c * w0_c + L0_n * w0_n)
        share_wage_bill0_n = (L0_n * w0_n) / (L0_c * w0_c + L0_n * w0_n)
        # Solve for employment levels
        employment0 = (L0_c + L0_n) * pop_count 
        employment0_c = L0_c * pop_count 
        employment0_n = L0_n * pop_count
        
        ## Payroll Tax Equilibrium ##
        #Solve for Payroll Tax rate
        #Let initial guess be based on Head Tax Wq
        t_guess = tau /(avg_prod1 - tau)
        #Define realized to fail condition at first
        t_realized = t_guess + t_epsilon + 1
        #Iterative algorithm to determine t
        iteration = 0
        while abs(t_guess - t_realized) >= t_epsilon:
            #If not initial guess, use last realized value
            if iteration>0: t_guess = t_realized
            #Calculate equilibrium values
            w2_c = A_c / (1+t_guess)
            w2_n = A_n / (1+t_guess)
            V2_c = w2_c + alpha_c * tau
            V2_n = w2_n + alpha_n * tau
            P2_c = (V2_c - kappa_lb) / kappa_dist
            P2_n = (V2_n - kappa_lb) / kappa_dist
            L2_c = P2_c * share_pop_c
            L2_n = P2_n * share_pop_n
            share_workers2_c = L2_c / (L2_c + L2_n)
            share_workers2_n =  L2_n / (L2_c + L2_n)
            avg_prod2 = share_workers2_c * A_c + share_workers2_n * A_n
            #Calculate resulting payroll tax
            t_realized = tau / (avg_prod2 - tau)
            #Add one to iteration count
            iteration=iteration+1
        t = t_realized
        # Solve for e-pop ratio in Payroll Tax Eq
        epop_ratio2 = L2_c + L2_n
        # Solve for wage bill share
        share_wage_bill2_c = (L2_c * w2_c) / (L2_c * w2_c + L2_n * w2_n)
        share_wage_bill2_n = (L2_n * w2_n) / (L2_c * w2_c + L2_n * w2_n)
        # Solve for employment levels
        employment2 = (L2_c + L2_n) * pop_count 
        employment2_c = L2_c * pop_count 
        employment2_n = L2_n * pop_count
                        
        # Store variables as attributes of object
        general_params = ['A_c', 'A_n', 'kappa_dist', 'kappa_lb', 'kappa_ub', 't']
        for var in general_params:
            exec("self."+var+"="+var)
            
        eq_values_w_type = ['w', 'V', 'P', 'L', 'share_workers', 'share_wage_bill', 'employment']
        for var in eq_values_w_type:
            for eq_num in ['0', '1', '2']:
                for _type in ['_c','_n']:        
                    exec("self."+var+eq_num+_type+'='+var+eq_num+_type)
        
        eq_values_wo_type = ['avg_prod', 'epop_ratio', 'employment']
        for var in eq_values_wo_type:
            for eq_num in ['0', '1', '2']:
                exec("self."+var+eq_num+'='+var+eq_num)

    ### Generate Tables in Tex ###
    def generate_table(self, file_name, year, table_type, table_label, location):
        
        ## Generate Summary Table
        if table_type=="equilibrium summary":
        
            ## Generate Strings that will be written into .tex file as a list
            header = [f'\ctable[caption={{Equilibrium Calibration for {year} with $\\alpha_C = {self.alpha_c}, \\alpha_N = {self.alpha_n}$}},', '\n',
            f'    label={table_label}, pos=h!]', '\n',
            '{cccccccc}{^{*}&{This represents an observed value.}}', '\n',
            '{\FL &&&&& \multicolumn{3}{c}{Equilibrium Values}  \\\\', '\n',
            '\cmidrule{6-8}', '\n',
            '   \multicolumn{2}{c}{General Parameters} &&&&  No ESHI  &  Head Tax  & Payroll Tax  \\\\', '\n',
            '\cmidrule{1-8}', '\n']
    
            table_values = [f'$A_C$ & {self.A_c:,.0f} &&&', '\n',
                f'$w_C$ & {self.w0_c:,.0f} & {self.w1_c:,.0f}\\tmark[*] & {self.w2_c:,.0f} \\\\', '\n',
                f'$A_N$ & {self.A_n:,.0f} &&&', '\n',
                f'$w_N$ & {self.w0_n:,.0f} & {self.w1_n:,.0f}\\tmark[*] & {self.w2_n:,.0f} \\\\', '\n',
                f'$\\tau$ & {self.tau:,.0f}\\tmark[*] &&&', '\n',
                f'$w_C/w_N$ & {self.w0_c/self.w0_n:,.3f} & {self.w1_c/self.w1_n:,.3f} & {self.w2_c/self.w2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'$N_C$ & {self.share_pop_c:,.3f}\\tmark[*] &&&', '\n',
                f'$P_C$ & {self.P0_c:,.3f} & {self.P1_c:,.3f} & {self.P2_c:,.3f} \\\\', '\n',
                f'$N_N$ & {self.share_pop_n:,.3f}  &&&', '\n',
                f'$P_N$ & {self.P0_n:,.3f} & {self.P1_n:,.3f} & {self.P2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                f'$\\overline{{\kappa}}$ & {self.kappa_ub:,.0f} &&&', '\n',
                f'$L_C$ & {self.L0_c:,.3f} & {self.L1_c:,.3f} & {self.L2_c:,.3f} \\\\', '\n',
                f'$\\underline{{\kappa}}$ &  {self.kappa_lb:,.0f} &&&', '\n',
                f'$L_N$ & {self.L0_n:,.3f} & {self.L1_n:,.3f} & {self.L2_n:,.3f} \\\\', '\n',
                f'$(\\overline{{\kappa}} - \\underline{{\kappa}})$ & {self.kappa_dist:,.0f} &&&', '\n',
                f'$L_C/L_N$ & {self.L0_c/self.L0_n:,.3f} & {self.L1_c/self.L1_n:,.3f} & {self.L2_c/self.L2_n:,.3f}  \\\\', '\n',
                '\\\\\n',
                f'Payroll Tax & {self.t * 100:,.2f}\\% &&&', '\n',
                f'$\\tilde{{A}}$ & {self.avg_prod0:,.0f} & {self.avg_prod1:,.0f} & {self.avg_prod2:,.0f} \\\\', '\n',
                '\\\\\n',
                f'Pop. Count & {self.pop_count:,.0f}\\tmark[*] &&&', '\n',
                f'E:P Ratio & {self.epop_ratio0:,.3f} & {self.epop_ratio1:,.3f}\\tmark[*] & {self.epop_ratio2:,.3f} \\\\', '\n', 
                '\\\\\n',
                '& &&& Share of Workforce \\\\', '\n',
                f'& &&& \\indent \\footnotesize College & {self.share_workers0_c:,.3f} & {self.share_workers1_c:,.3f}\\tmark[*] & {self.share_workers2_c:,.3f} \\\\', '\n',
                f'& &&& \\indent \\footnotesize Non-college & {self.share_workers0_n:,.3f} & {self.share_workers1_n:,.3f} & {self.share_workers2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                '& &&& Share of Wage Bill \\\\', '\n',
                f'& &&& \\indent \\footnotesize College & {self.share_wage_bill0_c:,.3f} & {self.share_wage_bill1_c:,.3f} & {self.share_wage_bill2_c:,.3f} \\\\', '\n',
                f'& &&& \\indent \\footnotesize Non-college & {self.share_wage_bill0_n:,.3f} & {self.share_wage_bill1_n:,.3f} & {self.share_wage_bill2_n:,.3f} \\\\', '\n',
                '\\\\\n',
                '& &&& Employment (Thous.) \\\\', '\n',
                f'& &&& \\indent \\footnotesize College & {self.employment0_c/1000:,.0f} & {self.employment1_c/1000:,.0f} & {self.employment2_c/1000:,.0f} \\\\', '\n',
                f'& &&& \\indent \\footnotesize Non-college & {self.employment0_n/1000:,.0f} & {self.employment1_n/1000:,.0f} & {self.employment2_n/1000:,.0f} \\\\', '\n']

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
            print("Fix this")
    
    
#%%  Create Instance #%%        
model = calibration_model(alpha_c=1, alpha_n=1,
                tau=8569, w1_c=88381, w1_n=47373,
                share_workers1_c=0.395, share_pop_c=0.357,
                epop_ratio1=0.624, pop_count=1e6)
model.calibrate()

model.generate_table(file_name='SummaryTable2018', year=2018, 
                     table_type="equilibrium summary", table_label="SummaryTable2018", 
                     location="/Users/caseymcquillan/Desktop")
