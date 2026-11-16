# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 12:34:02 2024

@author: thompson.3962

Using just the one angle value
"""
import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import pandas as pd
#from penetration_and_frensel import I0_alpha
from penetration_and_frensel import penetration_depth_dp
from penetration_and_frensel import alpha_list
from penetration_and_frensel import new_alpha_list
from penetration_and_frensel import folocal
from penetration_and_frensel import df
from penetration_and_frensel import true_range

"""
def tirf_model(params, x, alpha, p_alpha, I0_alpha):
    Cx, Zx, bx = params
    q = (Cx / p_alpha) * (1 - np.exp(-Zx * p_alpha)) + bx
    return q 

def residuals(params, x, alpha, p_alpha, I0_alpha, s_measured):
    return tirf_model(params, x, alpha, p_alpha, I0_alpha) - s_measured
"""
# Define the Top-Hat function
def top_hat_function(x, z, Cx, Zx):
    return Cx * (z <= Zx)

# Define the TIRF model
def tirf_model(x, alpha, Cx, Zx, bx, p_alpha, I0_alpha):
    Cx, Zx, bx = params
    return (1.0 / (p_alpha * I0_alpha)) * (1 - np.exp(-1.0 * p_alpha)) + 0.1

# Define the residuals for least-squares fitting
def residuals(params, x, alpha, s_measured, p_alpha, I0_alpha):
    Cx, Zx, bx = params
    s_predicted = tirf_model(x, alpha, 1.0, 1.0, 0.1, p_alpha, I0_alpha)
    return s_measured - s_predicted

# Extract a specific column (e.g., 'ColumnName')
column_data_distance = df['Distance_(pixels)']
x_data = column_data_distance * 66
s_x = pd.Series(x_data)
# Convert the Series to a NumPy array
x_data = s_x.to_numpy()


column_data_Gray_Value = df['Gray_Value']
s_measured = column_data_Gray_Value
s_m = pd.Series(s_measured)
# Convert the Series to a NumPy array
s_measured = s_m.to_numpy()

"""
#Cleaning up the nan's
df = pd.DataFrame({'yee': I0_alpha})
df = df.dropna()
yee_clean = df['yee'].values

df = pd.DataFrame({'qee': penetration_depth_dp})
df = df.dropna()
qee_clean = df['qee'].values

how_far = len(qee_clean)

#Take the length of the about penetration_depth_dp 
yee_clean42 = yee_clean[-how_far:]

x_data42 = x_data[-how_far:]

new_alpha_list42 = new_alpha_list[-how_far:]

s_measured42 = s_measured[-how_far:]
"""

bounds = (np.array([0, 0, 0]), np.array([np.inf, np.inf, np.inf]))
# Initial guess for Cx, Zx, bx
initial_guess = np.array([1.0, 1.0, 0.1])
#backup
result = least_squares(residuals, initial_guess, args=(x_data, new_alpha_list, 200, 1, s_measured), bounds=bounds)
# Extract the fitted parameters
Cx_fitted, Zx_fitted, bx_fitted = result.x
print("Optimization result:", result)



# Generate fitted data for visualization
s_fitted_list = []

# Fill the list with numbers from 1 to 10
for i in range(0, true_range):
    s_fitted = tirf_model([Cx_fitted, Zx_fitted, bx_fitted], x_data[i], new_alpha_list[i], 1.0, 1.0, 0.1, 65, 1)
    s_fitted_list.append(s_fitted)
    
# Print the list
print(s_fitted_list)

# Plot the measured data and the fitted model
plt.figure(figsize=(10, 6))
plt.plot(new_alpha_list, s_measured, 'o', label='Measured Data')
plt.plot(new_alpha_list, s_fitted_list, '-', label='Fitted Model')

plt.xlabel('Alpha')
plt.ylabel('Signal')
plt.title('TIRF Model Fitting')
plt.legend()
plt.savefig(folocal + 'TIRF MODEL FITTING.png')  # You can change the file name and format as needed

plt.show()

print(f"Fitted Cx: {Cx_fitted}")
print(f"Fitted Zx: {Zx_fitted}")
print(f"Fitted bx: {bx_fitted}")
