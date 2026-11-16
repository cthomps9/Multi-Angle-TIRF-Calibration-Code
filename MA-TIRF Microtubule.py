import numpy as np
import tifffile
from scipy.ndimage import gaussian_filter

volume = tifffile.imread('C:/Users/thompson.3962/Documents/MA_TIRF/Synthetic Images/10 Tubes Binned2.tif')
low_alpha = 61.8
high_alpha = 75.3485
num_ang = 31

# linear geometry
high_alpharad, low_alpharad = np.radians(high_alpha), np.radians(low_alpha)
D = 1/np.tan(low_alpharad)
d = (D - 1/np.tan(high_alpharad)) / (num_ang - 1)
tn = []
for n in range(num_ang):
    tn.append(np.arctan(1/(D - n * d)))
alpha = np.array(tn)
alpha = np.flip(alpha)
    
    
wavelength = 488
#n1 = 1.7786
n1 = 1.51
n2 = 1.33
n = n1 / n2
pen = wavelength / (4 * np.pi * np.sqrt(n1**2 * np.sin(alpha)**2 - n2**2))
ts = 2 * np.cos(alpha) / (np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
tp = 2 * n * np.cos(alpha) / (n**2 * np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
I0 = 0.75 * ts**2 + 0.25 * tp**2

sample = np.zeros((num_ang, volume.shape[1], volume.shape[2]), dtype=np.float32)
for j in range(num_ang):
    current_intensity = I0[j]
    silly = np.zeros((volume.shape[1], volume.shape[2]), dtype=np.float32)
    for z in range(volume.shape[0]):
        distance_from_interface = z
        evanescent_factor = np.exp(-distance_from_interface / pen[j])  # Evanescent wave decay

        # Apply the intensity and evanescent decay to the voxel values
        silly[:, :] += volume[z, :, :] * current_intensity * evanescent_factor
    sample[j, :, :] += silly

# Adding background noise
'''
mean_noise = 3000
std_noise = 300
sample = gaussian_filter(sample, sigma=1)
noise = np.random.normal(loc=mean_noise, scale=std_noise, size=sample.shape)
sample += noise
'''

tifffile.imwrite('C:/Users/thompson.3962/Documents/MA_TIRF/tubes/Sample.tif', sample)