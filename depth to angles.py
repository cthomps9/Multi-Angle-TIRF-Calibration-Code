# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 14:42:56 2025

This code was written to calculate the angle of the incidence beam into a 
pentration depth.ONce, snell's law had been used to determine the angle. 

@author: thompson.3962
"""
import math

def compute_tirf_angle_from_depth(d_nm, n1, n2, wavelength_nm):
    n1_sq = n1 ** 2
    n2_sq = n2 ** 2
    term = (wavelength_nm / (4 * math.pi * d_nm)) ** 2
    sin2_theta = (term + n2_sq) / n1_sq

    if sin2_theta >= 1.0:
        return None  # No physical solution

    sin_theta = math.sqrt(sin2_theta)
    theta_rad = math.asin(sin_theta)
    theta_deg = math.degrees(theta_rad)

    return theta_deg

# Parameters
n1 = 1.7786
n2 = 1.3300
wavelength_nm = 488

# List of penetration depths (nm)
depth_list = [75, 48, 48.7, 49.5, 50, 51, 52, 52.7, 53.5, 54.5, 55., 56.65, 57.5, 58.6, 60, 61, 62.5, 63.7, 65.3, 66.5, 66.9, 70.1, 70.5, 70.9,
              71.2, 72.1, 84.3, 88.2, 106.3, 108.4, 131.0, 132.3, 133.5, 135.0, 136, 138.7, 155.9, 171.3, 206.5, 230.3]

# Compute and store only the angles
angle_list = [
    compute_tirf_angle_from_depth(depth, n1, n2, wavelength_nm)
    for depth in depth_list
]

print(angle_list)

