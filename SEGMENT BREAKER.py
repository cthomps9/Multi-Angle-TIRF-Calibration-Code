# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 13:39:39 2024

This Python script list the highest critical angle possible and the lowest angle possible and tries to
map the segmentation of the SLM values. Then tries to take the SLM values new angle at face value.
These new angles are used to calculate pentration depth.After converting these angles to radians, it applies the
 electromagnetic decay formula to calculate the depth  in nanometers. The final output is a clear, labeled line 
 graph that demonstrates the fundamental TIRF principle: as the incident angle 
increases, the penetration depth into the specimen decreases, allowing for highly selective, near-surface imaging.

@author: thompson.3962
"""
import numpy as np
import matplotlib.pyplot as plt

def format_to_two_decimals(number):
    return [round(num, 2) for num in number]

def invert_list(lst):
    return lst[::-1]


# Define the range
start =  80
end = 61.8

n_1 = 1.51
n_2 = 1.33

# Generate 33 segments within the range
segments = np.linspace(start, end, 20)
# Reverse to get the angles sorted from smallest to largest
sg = format_to_two_decimals(segments[::-1])

insg = invert_list(sg)

print(insg)
# Convert angles to radians
sg_radians = np.radians(sg)
# Calculate penetration depth (z) for each angle
d = 488 / (4 * np.pi * np.sqrt((n_1**2) * (np.sin(sg_radians)**2) - (n_2**2)))

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(sg, d, '-', color='red', label='TIRF penetration depth')
plt.xlabel('Angles (degrees)')
plt.ylabel('Penetration Depth z (nm)')
plt.title('TIRF Model')
plt.legend()
plt.grid(True)
plt.show()
