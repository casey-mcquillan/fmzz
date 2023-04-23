#################################################################
#################################################################
###### FMZZ Replication Files for                      ##########
###### "The Health Wedge and Labor Market Inequality"  ##########
#################################################################
#################################################################

#################################################################
###### Authors ##################################################
This paper is authored by Amy Finkelstein, Casey McQuillan, Owen Zidar, and Eric Zwick and benefitted from excellent research assistance from Emily Bjorkman, Drew Burd, Patrick Collard, Coly Elhai, Dean Li, and Dustin Swonder.

This repository contains all the relevant code, but for the full the replication files, please contact Casey McQuillan at caseycm@princeton.edu


#################################################################
###### Github Repository ########################################
The code repository can be found here: https://github.com/casey-mcquillan/fmzz


#################################################################
### Section _: Set up and fundamentals  #########################
# __fmzz.py #
This file will execute all relevant code files to pull data, clean data, and generate tables.

# _set_directory.py #
This file defines the directory for all other files in this project. The "main_folder" be the FMZZ replication files folder. This folder will have the following subfolders: "code", "data", and "output". The "output" folder should also have a subfolder titled "Appendix".

# _baseline_specifications.py #
This file specifices baseline parameters for the main model such as the difference in group-specific amenity values (alpha_diff_baseline), baseline year, comparison past year, tau series to use, subsitutability parameter (rho), and elasticities.

# _varying_parameters.py #
This file specifies how different parameters such at tau, elasticity, and rho can/will be varied for robustness analysis.

# _fmzz_calibration_model.py #
This is the main calibration model, it uses assumptions based on differences in alpha, rho, tau, and elasticities as well as observed values of wages, employment rates, and shares of college and  non-college workers to calculate the Head Tax and Payroll Tax eq. For full details, please refer to the paper.

# _fmzz_calibration_model_CCF.py #
This file adjusts the main calibration model to allow for comparisons across equilibria for a counterfactual value of tau. In order to do so, it requires an assumption on alpha for both groups instead of just the difference in these values as well as a counterfactual value of tau.

# _fmzz_calibration_model_bySex.py #
This file adjusts the main calibration model to treat male and female workers as separate groups in order to decompose the effects of different ESHI financing schemes on each subgroup. Relative to the baseline model, it is necessary to specify wages, employment rates, and shares by both education (college and non-college) as well as sex (male and female).

# _fred_api_key.py #
This file specifices the FRED api key to be used when pulling data in the file "1a_pull_PCEPI.py".


#################################################################
### Section 1: Data Pulling and Cleaning  #######################

# 1a_pull_PCEPI.py #
This file pulls in data on PCE deflator from the St. Louis FRED and generates the file 'PCEPI_data.csv'. Note that it uses a FRED api key specified in "_fred_api_key.py"

# 1b_pull_OECD_data.py #
This file pulls in data on population level and employment rate from the St. Louis FRED and generates the file 'clean_OECD_data.csv'. Note that it uses a FRED api key specified in "_fred_api_key.py"

# 1c_clean_ASEC_data.py #
This cleans 'raw_ASEC_data.csv' in order to calculate employment rate, wages, and health insurance variables by year. This file outputs 'clean_ASEC_data.csv'.

# 1d_compile_observed_data.py #
This file combines 'clean_OECD_data.csv', 'clean_ASEC_data.csv', and 'premium_series.xlsx' in order to generate the file 'observed_data.csv' that contains all necessary data to calibrate the baseline model.

# 1e_Constructing_CCF.py #
This file uses 'observed_data.csv' as well as 'health_spending.csv' in order to output 'observed_data_CCF.csv', which is structured similarly to 'observed_data.csv', but with the addition of a counterfactual tau as described in the paper.


#################################################################
### Section 2: Generate Main Tables  ############################

# 2a_SummaryStats.py #
This code uses 'raw_ASEC_data.csv' as well as 'clean_OECD_data.csv' in order to generate "SummaryStats.tex", which are the summary statistics featured in Table 1 of the paper.

# 2b_EquilibriumComparison.py #
This code uses 'observed_data.csv' in order to generate "EquilibriumComparison.tex" which represents Table 3 of the paper.

# 2c_EquilibriumComparison_Robustness.py #
This code uses 'observed_data.csv' in order to generate "EquilibriumComparison_Robustness.tex" which represents Table 4 of the paper.

# 2d_CounterfactualGrowth.py #
This code uses 'observed_data.csv' in order to generate "CounterfactualGrowth.tex" which represents Table 5 of the paper.

# 2e_CounterfactualGrowth_Robustness.py #
This code uses 'observed_data.csv' in order to generate "CounterfactualGrowth_Robustness.tex" which represents Table 6 of the paper.

# 2f_EquilibriumComparison_CCF.py #
This code uses 'observed_data_CCF.csv' in order to generate "EquilibriumComparison_CCF.tex" which represents Table 7 of the paper.

# 2g_gen_figure1.py #
This code uses 'observed_data.csv' in order to generate "fig_2.xlsx" which is used to generate Figure 2 in the paper.


#################################################################
### Section RC1: Alternative College Definitions  ###############
# Note: This robustness check is intended to test whether the results of the main analysis are robust to different definitions of "college"

# RC1a_clean_ASEC_data.py #
This code uses 'raw_ASEC_data.csv' to generate 'RC1_clean_ASEC_data.csv', which is similar in structure to 'clean_ASEC_data.csv' but uses an alternative definition of college-educated worked which now includes workers with some college but not a Bachelor's degree or more.

# RC1b_compile_observed_data.py #
This file combines 'clean_OECD_data.csv', 'RC1_clean_ASEC_data.csv', and 'premium_series.xlsx' in order to generate the file 'RC1_observed_data.csv' that contains all necessary data to calibrate the baseline model.

# RC1c_SummaryStats.py #
This code uses 'raw_ASEC_data.csv' as well as 'clean_OECD_data.csv' in order to generate "RC1_SummaryStats.tex", which use the broader definition of "college" and are the summary statistics featured in Table A.1 of the appendix of the paper.

# RC1d_EquilibriumComparison.py #
This code uses 'RC1_observed_data.csv' in order to generate "RC1_EquilibriumComparison.tex" which is featured in Table A.2 of the appendix of the paper.

# RC1e_CounterfactualGrowth.py #
This code uses 'RC1_observed_data.csv' in order to generate "RC1_CounterfactualGrowth.tex" which is featured in Table A.3 of the appendix of the paper.

# RC1f_gen_figureA3.py #
This code uses 'observed_data.csv' in order to generate "fig_a3.xlsx" which is used to generate Figure A.3 of the appendix of the paper.


#################################################################
### Section RC2: Alternative College Definitions  ###############
# Note: This robustness check is intended to explore whether the results of the main analysis change when extending the analysis to consider education (college versus non-college) as well as sex (male versus female).

# RC2a_clean_ASEC_data_bySex.py #
This code uses 'raw_ASEC_data.csv' to generate 'RC2_clean_ASEC_data_bySex.csv', which is similar in structure to 'clean_ASEC_data.csv' but decomposes wages, employment rates and shares by both education (college versus non-college) as well as sex (male versus female).

# RC2b_compile_observed_data_bySex.py #
This file combines 'clean_OECD_data.csv', 'RC2_clean_ASEC_data.csv', and 'premium_series.xlsx' in order to generate the file 'RC2_observed_data.csv' that contains all necessary data to calibrate the extended model broken down by sex.

# RC2c_EquilibriumComparison_bySex.py #
This code uses 'RC2_observed_data_bySex.csv' in order to generate "RC2_EquilibriumComparison_bySex.tex" which is Table A.3 in the appendix of the paper.

# RC2d_CounterfactualGrowth_bySex.py #
This code uses 'RC2_observed_data_bySex.csv' in order to generate "RC2_CounterfactualGrowth_m.tex" and "RC2_CounterfactualGrowth_f.tex" which are Tables A.5 and A.6 respectively in the appendix of the paper.


#################################################################
###### MIT License ##############################################

Copyright (c) 2021 Casey McQuillan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.