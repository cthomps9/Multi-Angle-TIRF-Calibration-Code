import numpy as np
import tifffile as tiff

# Parameters
volume_size = (500, 500, 500)  # (z, y, x)
num_microtubules = 1
tube_radius = 5  # pixels
intensity = 255  # max brightness
edge_margin = 20  # margin before forcing direction change
z_steps_per_turn_min = 200
z_steps_per_turn_max = 500
attraction_strength = 0.1  # Strength of the attraction force
attraction_radius = 50  # Max distance for attraction

# Create empty volume
volume = np.zeros(volume_size, dtype=np.uint16)

# List to store the positions of the microtubules (x, y, z)
tube_positions = []

def draw_individual_tube(volume, x, y, z, radius, intensity):
    """Draw an individual microtubule as a circle in the z-slice."""
    x = int(x)
    y = int(y)
    z = int(z)

    if 0 <= x < volume.shape[2] and 0 <= y < volume.shape[1] and 0 <= z < volume.shape[0]:
        for dy in range(-radius, radius+1):
            for dx in range(-radius, radius+1):
                if dx**2 + dy**2 <= radius**2:
                    zx, zy = x + dx, y + dy
                    if 0 <= zx < volume.shape[2] and 0 <= zy < volume.shape[1]:
                        volume[z, zy, zx] += intensity

def apply_attraction(x, y, z, tube_positions, attraction_strength, attraction_radius):
    """Apply attraction force towards nearby tubes."""
    force_dx, force_dy = 0, 0
    
    for (tx, ty, tz) in tube_positions:
        # Calculate distance between current tube and previous tube
        dist = np.sqrt((x - tx)**2 + (y - ty)**2 + (z - tz)**2)
        
        # If within attraction radius, apply force
        if dist < attraction_radius:
            # The attraction force decreases with distance
            attraction_factor = attraction_strength * (attraction_radius - dist) / attraction_radius
            # Apply force proportional to the direction vector between the two tubes
            force_dx += attraction_factor * (tx - x)
            force_dy += attraction_factor * (ty - y)
    
    return force_dx, force_dy

for m in range(num_microtubules):
    # Random starting point
    x = np.random.randint(volume_size[2]//2 - 30, volume_size[2]//2 + 30)
    y = np.random.randint(volume_size[1]//2 - 30, volume_size[1]//2 + 30)
    z = 0

    # Random initial direction
    angle = np.random.uniform(0, 2*np.pi)
    dx = np.cos(angle)
    dy = np.sin(angle)

    steps_until_turn = np.random.randint(z_steps_per_turn_min, z_steps_per_turn_max)

    # Store the initial position
    tube_positions.append((x, y, z))

    while z < volume_size[0]:
        # Apply attraction force to the current tube
        force_dx, force_dy = apply_attraction(x, y, z, tube_positions, attraction_strength, attraction_radius)

        # Adjust direction based on the attraction force
        dx += force_dx
        dy += force_dy
        
        # Normalize the direction to prevent runaway values
        norm = np.sqrt(dx**2 + dy**2)
        if norm != 0:
            dx /= norm
            dy /= norm

        # Draw current position as part of the tube (independently)
        draw_individual_tube(volume, x, y, z, tube_radius, intensity)

        # Move in the adjusted direction of the tube
        x += dx
        y += dy
        z += 1

        # Boundary checking
        if x < edge_margin or x >= volume_size[2] - edge_margin or y < edge_margin or y >= volume_size[1] - edge_margin:
            old_angle = np.arctan2(dy, dx)
            new_angle = old_angle + np.pi + np.random.uniform(-np.pi/4, np.pi/4)
            dx = np.cos(new_angle)
            dy = np.sin(new_angle)
            steps_until_turn = np.random.randint(z_steps_per_turn_min, z_steps_per_turn_max)

        # Randomly change direction after some steps
        steps_until_turn -= 1
        if steps_until_turn <= 0:
            delta_angle = np.random.uniform(-np.pi/6, np.pi/6)
            current_angle = np.arctan2(dy, dx)
            new_angle = current_angle + delta_angle
            dx = np.cos(new_angle)
            dy = np.sin(new_angle)
            steps_until_turn = np.random.randint(z_steps_per_turn_min, z_steps_per_turn_max)

    # Store the final position of this tube
    tube_positions.append((x, y, z))

# Save as multipage TIFF
tiff.imwrite('C:/Users/hirka/Kural/Data Analysis/MA-SIM/Synthetic/' + str(num_microtubules) + ' Tubes.tif', volume)
print('Synthetic microtubule TIF saved!')





'''
from mayavi import mlab

# Load volume
volume = tiff.imread('C:/Users/hirka/Kural/Data Analysis/MA-SIM/Synthetic/Synthetic Tube.tif')
volume = volume.astype(np.float32) / 255.0


mlab.figure(size=(800, 800), bgcolor=(0, 0, 0))  # black background for glowing effect
src = mlab.pipeline.scalar_field(volume)

# Apply volume rendering
mlab.pipeline.volume(src, vmin=0.2, vmax=0.8)  # adjust vmin/vmax to tune glow
mlab.orientation_axes()
mlab.show()
'''