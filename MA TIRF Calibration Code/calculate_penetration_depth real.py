# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 16:01:45 2024

@author: thompson.3962
"""
import math

def calculate_penetration_depth(wavelength, n1, n2, theta):
    """
    Calculate the penetration depth in TIRF microscopy.

    Parameters:
    wavelength (float): Wavelength of the incident light (in nm).
    n1 (float): Refractive index of the medium through which the light is traveling.
    n2 (float): Refractive index of the medium into which the light would be refracted.
    theta (float): Angle of incidence of the light (in degrees).

    Returns:
    float: Penetration depth (in nm).
    """
    # Convert angle from degrees to radians
    theta_rad = math.radians(theta)
    
    # Calculate the penetration depth using the given equation
    try:
        penetration_depth = wavelength / (4 * math.pi * math.sqrt(n1**2 * math.sin(theta_rad)**2 - n2**2))
        return penetration_depth
    except ValueError:
        return "Invalid input values leading to math domain error."

# Example usage
wavelength = 488  # nm
n1 = 1.51  # Refractive index of glass
n2 = 1.33  # Refractive index of water
theta = 61.74  # degrees

penetration_depth = calculate_penetration_depth(wavelength, n1, n2, theta)
print(penetration_depth)

