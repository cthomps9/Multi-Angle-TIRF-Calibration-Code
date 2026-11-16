import numpy as np
import pandas as pd
from scipy.optimize import least_squares, differential_evolution, NonlinearConstraint
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import tifffile
import os
import glob
import string
import random
import time
############### Main Parame/ers ###############
folocal = 'D:/20240212_Lens_FrameWork/Thin Exp 1 Power 0.7/'
stackpath = folocal + 'AVG_combined_stack-2.tif'
stack = tifffile.imread(stackpath)
sz, sy, sx = np.shape(stack)

xval = np.linspace(0, sx - 1, sx)
#xval = np.linspace(250, 420, 171)
# Pot Belly EXP 1: xxx to xxx
# Pot Belly EXP 2: xxx to xxx
# Pot Belly EXP 3: xxx to xxx
# Thin EXP 1: 175 to 410 (236), 1 through 18
# Thin EXP 2: 220 to 455 (236), 1 through 18
# Thin EXP 3: 285 to 520 (236), 1 through 18

xval = np.linspace(890, 900, 51)
#yval = np.linspace(-149, 149, 100)

yval = np.linspace(-150, 149, 300)

def tirf_model(alpha, Cx, Zx, bx, stretch):
    wavelength = 488
    n1 = 1.51
    n2 = 1.33
    n = n1 / n2
    #alpha = stretch * alpha
    p_alpha = 1/(wavelength / (4 * np.pi * np.sqrt(n1**2 * np.sin(alpha)**2 - n2**2)))
    ts = 2 * np.cos(alpha) / (np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
    tp = 2 * n * np.cos(alpha) / (n**2 * np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
    I0 = 0.75 * ts**2 + 0.25 * tp**2
    return (Cx / p_alpha) * I0 * (1 - np.exp(-Zx * p_alpha)) + bx

def tirf_model_2(params, alpha):
    Cx, Zx, bx, stretch = params
    wavelength = 488
    n1 = 1.51
    n2 = 1.33
    n = n1 / n2
    #alpha = stretch * alpha
    p_alpha = 1/(wavelength / (4 * np.pi * np.sqrt(n1**2 * np.sin(alpha)**2 - n2**2)))
    ts = 2 * np.cos(alpha) / (np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
    tp = 2 * n * np.cos(alpha) / (n**2 * np.cos(alpha) + np.sqrt(n**2 - np.sin(alpha)**2))
    I0 = 0.75 * ts**2 + 0.25 * tp**2
    return (Cx / p_alpha) * I0 * (1 - np.exp(-Zx * p_alpha)) + bx

def residuals(params, s_obs, alpha):
    Cx, Zx, bx, stretch = params
    s_pred = tirf_model_2(params, alpha)
    return s_obs - s_pred

# Begin taking Zx estimates for each x in xval
def find_angle(params, yval, xval, sx, stack):
    high_alpha, low_alpha = params
    alpha = np.linspace(high_alpha, low_alpha, np.shape(stack)[0])
    alpha = np.radians(alpha)
    
    bigZ2s = []
    s_measured_y = np.empty((len(yval), len(alpha)))
    bounds = [(0, np.inf), (0, np.inf), (0, np.inf), (0, np.inf)]
    for xtrial in xval:
        county = 0
        for ytrial in yval:
            s_measured_y[county, :] = stack[:, sy//2 + int(ytrial), int(xtrial)]
            county += 1
        s_measured = np.mean(s_measured_y, axis=0)
        
        initial_guess = np.array([1, 500, 140, 1])
        try:
            result = least_squares(residuals, initial_guess, args=(s_measured, alpha),
                                   jac = '2-point', method = 'lm', max_nfev=5000)
            Cx_fitted2, Zx_fitted2, bx_fitted2, stretch_fitted2 = result.x
        except:
            Cx_fitted2, Zx_fitted2, bx_fitted2, stretch_fitted2 = np.nan, np.nan, np.nan, np.nan
        bigZ2s.append(Zx_fitted2)
        """
        s_fitted = tirf_model(alpha, Cx_fitted2, Zx_fitted2, bx_fitted2, stretch_fitted2)
        ss_res = np.sum((s_measured - s_fitted) ** 2)
        ss_tot = np.sum((s_measured - np.mean(s_measured)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        alpha_deg = np.degrees(alpha)
        plt.figure(figsize=(10, 6))
        plt.plot(alpha_deg, s_measured, 'o', label='Measured Data')
        plt.plot(alpha_deg, s_fitted, '-', label='Fitted Model')
        plt.xlabel('Alpha')
        plt.ylabel('Signal')
        plt.title(f'x = {int(xtrial)} px, z = {Zx_fitted2:.2f} nm')
        plt.legend()
        plt.show()
        """
    localZs = np.array(bigZ2s)
    localXs = xval * 34
    m, b = np.polyfit(localXs, localZs, 1)
    fit = np.polyval((m, b), localXs)
    ss_res = np.sum((localZs - fit) ** 2)
    ss_tot = np.sum((localZs - np.mean(localZs)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    angle = np.degrees(np.arctan(m))
    return angle, m, b, bigZ2s, r_squared


initial_guess_comert = [79.47, 61.8]
angle, m, b, bigZ2s, r_squared = find_angle(initial_guess_comert, yval, xval, sx, stack)
plt.figure(figsize=(10, 6))
plt.plot(xval, bigZ2s, '-', color='red', label='LM method')
plt.plot(xval, m * xval * 34 + b, '--', color='blue', label=f'Angle = {angle:.4f}\N{DEGREE SIGN}\n$R^2 = {r_squared:.4f}$')
plt.xlabel('x (px)')
plt.ylabel('z (nm)')
plt.title('TIRF Model Fitting')
plt.legend()
plt.grid(True)
plt.savefig(folocal + 'TIRF Model Fitting.png')  # You can change the file name and format as needed
plt.show()
stop
def angle_optimize(params, yval, xval, sx, stack, folocal, row_count):
    angle, m, b, bigZ2s, r_squared = find_angle(params, yval, xval, sx, stack)
    angle_data = pd.DataFrame([[params[1], params[0], angle, r_squared]], columns=['Lower Alpha', 'Upper Alpha', 'Angle', 'Fit'])
    angle_data.to_csv(folocal + 'Angle Data.csv', mode='a', header=False, index=False)
    row_count[0] += 1
    if row_count[0] >= 1250:
        print(f'\rRow {row_count[0]} Angle Range: {params[1]:.4f} to {params[0]:.4f} --> {angle:.4f}\N{DEGREE SIGN}, Fit = {r_squared:.4f}', end = ' ')
        raise ValueError("Reached maximum data points. Restarting optimization.")
    print(f'\rRow {row_count[0]} Angle Range: {params[1]:.4f} to {params[0]:.4f} --> {angle:.4f}\N{DEGREE SIGN}, Fit = {r_squared:.4f}', end='')
    return np.abs(angle - np.degrees(np.arctan(34/66)))

# for thin side, target angle is arctan(4.5/66), or 3.9005 degrees
# for pot-belly side, target angle is arctan(34/66), or 27.2553 degrees

bounds = [(61.77, 89.99), (61.77, 89.99)]
bounds = [(61.77, 90), (61.77, 66)]
constraint = NonlinearConstraint(lambda params: params[0] - params[1], 0, np.inf)
maxiter = 25 # 20 for (61.77, 66), 3 for (62, 62.3), 2 for (61.77, 62)
for iii in range(maxiter):
    starttime = time.time()
    if iii == maxiter - 5:
        bounds = [(61.77, 90), (62, 62.3)]
    if iii == maxiter - 2:
        bounds = [(61.77, 90), (61.77, 62)]
    if os.path.exists(folocal + 'Angle Data.csv'):
        res = ''.join(random.choices(string.ascii_letters, k=10))
        os.rename(folocal + 'Angle Data.csv', folocal + 'Angle Data ' + str(res) + '.csv')
    row_count = [0]
    df = pd.DataFrame(columns=['Lower Alpha', 'Upper Alpha', 'Angle', 'Fit'])
    df.to_csv(folocal + 'Angle Data.csv', index=False)
    try:
        opti_result = differential_evolution(angle_optimize, bounds, args=(yval, xval, sx, stack, folocal, row_count), constraints=(constraint,))
        #opti_ang = opti_result.x
    except:
        endtime = time.time()
        totaltime = int(endtime - starttime)
        print(f'({totaltime//60} min {np.mod(totaltime, 60)} sec)')
    if iii == maxiter - 1:
        stop

if os.path.exists(folocal + 'Angle Data.csv'):
    res = ''.join(random.choices(string.ascii_letters, k=10))
    os.rename(folocal + 'Angle Data.csv', folocal + 'Angle Data ' + str(res) + '.csv')

file_pattern = folocal + 'Angle Data*.csv'
file_list = glob.glob(file_pattern)
dataframes = [pd.read_csv(file) for file in file_list]
combined_data = pd.concat(dataframes, ignore_index=True)
combined_data.to_csv(folocal + 'Total Angle Data.csv', index=False)
x = combined_data['Lower Alpha']
y = combined_data['Upper Alpha']
color_values = combined_data['Angle']
target = np.degrees(np.arctan(4.5/66))
threshold = 0.1
colors = []
# There's gotta be an easier way than this...
for val in color_values:
    distance = abs(val - target)
    if distance > threshold:
        colors.append((1, 0, 0))
    elif 0.5 * threshold < distance <= threshold:
        green_intensity = (threshold - distance) / (0.5 * threshold)
        colors.append((1, green_intensity, 0))  # Red at 1, green inc --> red to yellow
    elif distance <= 0.5 * threshold:
        red_intensity = distance / (0.5 * threshold)
        colors.append((red_intensity, 1, 0))  # Green at 1, red dec --> yellow to green
plt.figure(figsize=(15, 9))
plt.scatter(x, y, color=colors, s=1)
plt.xlabel('Lower Alpha')
plt.ylabel('Upper Alpha')
plt.xlim(61.77, 63.5)
plt.ylim(61.77, 90)
plt.title('Angle Space for Thin Side EXP 2')
plt.savefig(folocal + 'Angle Space for Thin Side EXP 2.png')
plt.show()


base_folder = 'C:/Users/hirka/Kural/Data Analysis/Phantom Sample'
file_pattern = os.path.join(base_folder, '**', 'Total Angle Data.csv')
file_list = glob.glob(file_pattern, recursive=True)
target = np.degrees(np.arctan(4.5 / 66))
threshold = 0.1
smoothing_factor = 0.2
colors = plt.cm.brg(np.linspace(0, 1, len(file_list)))
x_fit_all = []
y_fit_all = []
plt.figure(figsize=(15, 9))
for idx, file_path in enumerate(file_list):
    data = pd.read_csv(file_path)
    #image_file = os.path.dirname(file_path) + '/AVG_combined_stack2.tif'
    #sz, sy, sx = np.shape(tifffile.imread(image_file))
    data['distance'] = abs(data['Angle'] - target)
    filtered_data = data[data['distance'] <= threshold]
    x = filtered_data['Lower Alpha']
    y = filtered_data['Upper Alpha']
    #spacing = (y - x)/(sz - 1)
    #retract = sz - 14
    #x = x + spacing * retract
    sorted_indices = np.argsort(x)
    x = x.iloc[sorted_indices].values
    y = y.iloc[sorted_indices].values
    spline_fit = UnivariateSpline(x, y, s=smoothing_factor * len(x))
    x_fit = np.linspace(x.min(), x.max(), 2000)
    y_fit = spline_fit(x_fit)
    x_fit_all.append(x_fit)
    y_fit_all.append(y_fit)
    y_pred = spline_fit(x)
    residue = y - y_pred
    residual_std = np.std(residue)
    ss_res = np.sum(residue ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    y_fit_upper = y_fit + residual_std
    y_fit_lower = y_fit - residual_std
    label = f'{os.path.basename(os.path.dirname(file_path))} (R² = {r_squared:.3f})'
    #plt.scatter(x, y, color=colors[idx], alpha=0.1, s=1)
    plt.fill_between(x_fit, y_fit_lower, y_fit_upper, color=colors[idx], alpha=0.2)
    plt.plot(x_fit, y_fit, label=label, color=colors[idx])

min_distance = np.inf
closest_x = None
closest_y = []
for i in range(len(x_fit_all[0])):  
    total_distance = 0
    y_at_x = []
    for j in range(len(file_list)):
        y_at_x.append(np.interp(x_fit_all[0][i], x_fit_all[j], y_fit_all[j]))
    for k in range(len(y_at_x)):
        for l in range(k + 1, len(y_at_x)):
            total_distance += abs(y_at_x[k] - y_at_x[l])
    if total_distance < min_distance:
        min_distance = total_distance
        closest_x = x_fit_all[0][i]
        closest_y = y_at_x
closest_y = np.mean(np.array(closest_y))
plt.scatter(closest_x, closest_y, color='black', zorder=5, label=f'Closest Point:\n$\\alpha$ = ({closest_x:.4f}, {closest_y:.4f})')

plt.xlabel('Lower Alpha')
plt.ylabel('Upper Alpha')
plt.title('Angle Data For Thin Side')
plt.xlim(61.77, 63.5)
plt.ylim(61.77, 90)
plt.legend()
plt.savefig(base_folder + '/Total Angle Space.png')
plt.show

print(f'{closest_x}, {closest_y}')