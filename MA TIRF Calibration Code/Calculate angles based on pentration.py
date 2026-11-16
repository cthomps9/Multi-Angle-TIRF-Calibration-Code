# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 11:14:04 2025

@author: thompson.3962
"""
import math

# Constants
lambda_ = 488e-9  # 488 nm in meters
n1 = 1.3355
n2 = 1.7786

# Function to compute incident angle in degrees for a given penetration depth
def compute_incident_angle(dp_target, lambda_, n1, n2):
    term = (lambda_ / (4 * math.pi * dp_target))**2 + n1**2
    sin_theta_squared = term / n2**2
    sin_theta = math.sqrt(sin_theta_squared)
    theta_rad = math.asin(sin_theta)
    theta_deg = math.degrees(theta_rad)
    return theta_deg

# Function to handle a list of penetration depths
def compute_angles_for_list(dp_list, lambda_, n1, n2):
    return [compute_incident_angle(dp, lambda_, n1, n2) for dp in dp_list]

# Example list of penetration depths in meters
penetration_depths = [48e-9, 49.5e-9, 49.8e-9, 50e-9, 51e-9, 53e-9,
                      55e-9, 56e-9, 57e-9, 58e-9, 59e-9,
                      60e-9, 60.5e-9, 61e-9, 62e-9, 65e-9,
                      66e-9, 68e-9, 69e-9, 69.5e-9, 70.5e-9, 
                      71e-9, 78e-9, 80e-9, 82.5e-9, 86.5e-9,
                      93e-9, 95e-9, 98e-9, 100e-8, 105e-8,
                      115e-8, 123e-8, 128e-8, 138e-8, 150e-8,
                      155e-8, 183e-8, 200e-8]

# Compute angles for all penetration depths
angles = compute_angles_for_list(penetration_depths, lambda_, n1, n2)

print("Penetration depths (m):", penetration_depths)
print("Incident angles (deg):", angles)

