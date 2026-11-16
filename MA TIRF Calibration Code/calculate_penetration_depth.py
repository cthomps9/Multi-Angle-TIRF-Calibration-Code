# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 16:07:41 2024

@author: thompson.3962
"""
def increment_by_point_zero_one(start, count):
    """
    Increment a value by 0.01 from start and store in an array.

    Parameters:
    start (float): The starting value.
    count (int): The number of increments.

    Returns:
    list: Array of incremented values.
    """
    values = []
    current = start
    for _ in range(count):
        values.append(round(current, 2))
        current += 0.01
    return values

# Example usage
start_value = 2.47




increments_count = 20

incremented_values = increment_by_point_zero_one(start_value, increments_count)
print(incremented_values)