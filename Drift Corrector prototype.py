# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 12:38:21 2025

@author: thompson.3962
"""
import numpy as np
from skimage import registration, filters, io, exposure
from scipy.ndimage import shift
import matplotlib.pyplot as plt

class TIRFMDriftCorrector:
    def __init__(self, ref_img, mov_img):
        """
        Initialize drift corrector with reference and moving images.
        
        Args:
            ref_img: 2D numpy array - Reference TIRFM image.
            mov_img: 2D numpy array - Image to be aligned.
        """
        self.ref_img = ref_img.astype(np.float32)
        self.mov_img = mov_img.astype(np.float32)
        self.shift_vector = None
        self.registered_img = None

    def calculate_drift(self, upsample_factor=20):
        """
        Calculate subpixel drift between images.
        
        Args:
            upsample_factor: int - Precision factor (default: 20).
            
        Returns:
            tuple: (y_shift, x_shift) in pixels.
        """
        # Apply Gaussian filtering to smooth out noise
        ref_smooth = filters.gaussian(self.ref_img, sigma=1)
        mov_smooth = filters.gaussian(self.mov_img, sigma=1)

        # Normalize images to [-1, 1] as required by phase_cross_correlation
        ref_smooth = 2 * ((ref_smooth - np.min(ref_smooth)) / (np.max(ref_smooth) - np.min(ref_smooth))) - 1
        mov_smooth = 2 * ((mov_smooth - np.min(mov_smooth)) / (np.max(mov_smooth) - np.min(mov_smooth))) - 1

        # Compute phase cross-correlation shift
        try:
            shift_vec, _, _ = registration.phase_cross_correlation(
                reference_image=ref_smooth,
                moving_image=mov_smooth,
                upsample_factor=upsample_factor
            )
            self.shift_vector = shift_vec
            return shift_vec
        except Exception as e:
            print(f"Drift calculation failed: {str(e)}")
            return (0, 0)  # Return zero shift if calculation fails

    def correct_drift(self):
        """Apply the calculated drift correction."""
        if self.shift_vector is None:
            self.calculate_drift()

        # Apply shift with bilinear interpolation (faster than cubic)
        self.registered_img = shift(
            input=self.mov_img,
            shift=self.shift_vector,
            mode='reflect',
            order=1  # Bilinear interpolation (good balance of speed & quality)
        )
        return self.registered_img

    def visualize_results(self):
        """Show alignment results."""
        if self.registered_img is None:
            self.correct_drift()

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Original difference
        axes[0].imshow(np.abs(self.ref_img - self.mov_img), cmap='hot')
        axes[0].set_title(f'Before Correction\nShift: {self.shift_vector}')

        # Corrected difference
        axes[1].imshow(np.abs(self.ref_img - self.registered_img), cmap='hot')
        axes[1].set_title('After Correction')

        # Overlay
        axes[2].imshow(self.ref_img, cmap='Greens', alpha=0.5)
        axes[2].imshow(self.registered_img, cmap='Reds', alpha=0.5)
        axes[2].set_title('Overlay (Green=Ref, Red=Aligned)')

        plt.tight_layout()
        plt.show()

    def save_corrected_image(self, filename="aligned_image.tif"):
        """
        Save the corrected image with proper scaling.
        
        Args:
            filename: str - Path to save the output image.
        """
        if self.registered_img is None:
            self.correct_drift()

        # Normalize and rescale the image to uint16 format
        normalized_img = exposure.rescale_intensity(self.registered_img, out_range=(0, 65535))
        io.imsave(filename, normalized_img.astype(np.uint16))
        print(f"Saved corrected image as {filename}")

# Example usage
if __name__ == "__main__":
    try:
        # Load images (replace with your actual file paths)
        img65 = io.imread('62.tif').astype(np.float32)
        img70 = io.imread('65.tif').astype(np.float32)

        # Initialize and process
        corrector = TIRFMDriftCorrector(ref_img=img65, mov_img=img70)
        detected_shift = corrector.calculate_drift()
        print(f"Detected shift (y, x): {detected_shift} pixels")

        # Apply correction
        aligned_img = corrector.correct_drift()

        # Visual verification
        corrector.visualize_results()

        # Save result with proper scaling
        corrector.save_corrected_image("aligned_70deg.tif")

    except Exception as e:
        print(f"Error in drift correction: {str(e)}")
