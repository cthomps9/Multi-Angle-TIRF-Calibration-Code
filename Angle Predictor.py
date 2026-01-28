import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import tifffile as tiff

# Constants (you can adjust these values based on your specific setup)
n_coverglass = 1.51  # refractive index of coverglass 
n_medium = 1.33       # refractive index of the medium (e.g., water)

# Calculate the critical angle using Snell's law
theta_c = np.arcsin(n_medium / n_coverglass)

# Define an SNR model as a Gaussian function centered around the critical angle
def snr_model(angle, peak_snr=100, width=0.01):
    """
    Gaussian-like model for SNR as a function of angle.
    
    Arguments:
    - angle: Angle of incidence in radians
    - peak_snr: The peak SNR at the critical angle
    - width: Width of the Gaussian peak
    """
    return peak_snr * np.exp(-((angle - theta_c)**2) / (2 * width**2))


folocal = 'D:/2024111_More_lens_framework_BEST_Rotated_2/Thin lens 250ms exposure/EXP 1/'
stackpath = folocal + 'AVG_combined_stack-5.tif'

# Read the TIFF stack
filename = 'your_tiff_stack.tif'  # Replace with the path to your TIFF stack
with tiff.TiffFile(stackpath) as tif:
    tiff_stack = tif.asarray()  # Load the entire stack as a numpy array


height, width, num_frames = tiff_stack.shape


snr_values_stack = []

# Loop through each frame in the stack
for i in range(num_frames):

    img = tiff_stack[:, :, i]
    

    img = img.astype(np.float64)
    

    signal_mean = np.mean(img)
    noise_std = np.std(img)
    

    if noise_std > 0:
        snr = signal_mean / noise_std
    else:
        snr = np.nan  
    
    # Append the SNR for this image/frame to the stack of SNR values
    snr_values_stack.append(snr)

# Convert the list of SNR values to a numpy array for easy plotting
snr_values_stack = np.array(snr_values_stack)

# Plot the SNR values for each frame in the stack
plt.plot(range(num_frames), snr_values_stack, label="SNR from TIFF Stack")
plt.xlabel("Image Frame (Index)")
plt.ylabel("SNR")
plt.title("SNR vs. Frame for TIFF Stack")
plt.legend()
plt.grid(True)
plt.show()

# Function to predict the angle from a given target SNR using optimization
def predict_angle_from_snr(target_snr, peak_snr=100, width=0.01):
    """
    Predict the angle of incidence for a given SNR value.
    Uses optimization to minimize the difference between model and target SNR.
    
    Arguments:
    - target_snr: The desired target SNR
    - peak_snr: Peak SNR (default is 100)
    - width: Width of the Gaussian peak (default is 0.01)
    """
    def cost_function(angle):
        return np.abs(snr_model(angle, peak_snr, width) - target_snr)
    
    # Use scipy's minimize function to find the angle that minimizes the cost
    result = minimize(cost_function, theta_c, bounds=[(theta_c - 0.05, theta_c + 0.05)])
    
    return result.x[0]

# Example: Predict the angle for a specific target SNR from the first frame
target_snr = snr_values_stack[0]  # Use the SNR from the first frame as an example
predicted_angle = predict_angle_from_snr(target_snr)

print(f"Predicted angle for target SNR of {target_snr}: {np.degrees(predicted_angle):.2f}°")
