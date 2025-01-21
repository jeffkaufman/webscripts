#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.optimize import curve_fit

def exponential_decay(t, a, k):
    """Exponential decay function: a * exp(-k * t)

    Parameters:
    t : array-like, time values
    a : float, initial amplitude
    k : float, decay rate
    """
    return a * np.exp(-k * t)

cols = []

data = defaultdict(list)

with open("pm2.5.tsv") as inf:
    for line in inf:
        bits = line.rstrip("\n").split("\t")
        if not cols:
            cols = bits
            continue

        for colname, colvalue in zip(cols, bits):
            if colname == "minute":
                continue
            if not colvalue:
                continue

            data[colname].append(int(colvalue))

# Create figure for all plots
plt.figure(figsize=(12, 15))

OFFSET=3

def get_post_peak_subset(test_condition, test_points):
    # Find post-peak subset using last occurrence of peak
    peak_value = max(test_points)

    peak_idx = len(test_points) - 1 - test_points[::-1].index(peak_value)

    if test_condition == 'no purifiers':
        peak_idx += 4
    elif test_condition == 'window':
        peak_idx += 5


    post_peak_subset = test_points[peak_idx + OFFSET:]
    post_peak_time = np.arange(len(post_peak_subset))

    return peak_idx + OFFSET, post_peak_subset, post_peak_time


conditions = [
    'no purifiers',
    'vent',
    'window',
    'purifiers auto',
    'purifiers high',
    '2x purifiers auto',
    '2x purifiers auto + vent',
    '2x purifiers auto + 3pro/6',
]

condition_names = {
    'no purifiers': "Control",
    'vent': "Over-stove Vent",
    'window': "Open Window",
    'purifiers auto': "1x AP-1512 (auto)",
    'purifiers high': "1x AP-1512 (high)",
    '2x purifiers auto': "2x AP-1512 (auto)",
    '2x purifiers auto + vent': "2x AP-1512 (auto) + Over-stove Vent",
    '2x purifiers auto + 3pro/6': "2x AP-1512 (auto) + 1x 3Pro (6)",
}

print(sorted(data.keys()))

for idx, test_condition in enumerate(condition_names, 1):
    test_points = data[test_condition]

    while test_points[2] < 20:
        del test_points[0]


    # Create time array starting from 0
    time = np.arange(len(test_points))

    peak_offset_idx, post_peak_subset, post_peak_time = get_post_peak_subset(
        test_condition, test_points)

    # Fit exponential decay to post-peak data

    # Initial guess: a0 = max value, k0 = 0.1
    popt, pcov = curve_fit(exponential_decay, post_peak_time,
                         post_peak_subset,
                         p0=[max(post_peak_subset), 0.1])

    # Get fitted parameters
    a_fit, k_fit = popt

    # Calculate half-life
    half_life = np.log(2) / k_fit

    # Calculate R-squared
    residuals = post_peak_subset - exponential_decay(post_peak_time, a_fit,
    k_fit)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((post_peak_subset - np.mean(post_peak_subset))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # Create subplot in a 2-column grid
    rows = (len(data) + 1) // 2  # Ceiling division to handle odd numbers
    plt.subplot(rows, 2, idx)

    # Plot original data
    plt.scatter(time, test_points, label='Original Data', alpha=0.5)

    # Plot fitted curve
    fit_time = np.linspace(0, len(post_peak_subset), 100)
    plt.plot(fit_time + peak_offset_idx,
            exponential_decay(fit_time, a_fit, k_fit),
            'r-', label='Fitted Decay')

    plt.ylim(ymin=0, ymax=900)
    plt.xlim(xmin=0, xmax=60)

    plt.title(f'{condition_names[test_condition]}\n'
              f'Decay = {k_fit:.4f}/min, '
              f'Half-life = {half_life:.1f} min, R² = {r_squared:.2f}')
    plt.xlabel('Time (minutes)')
    plt.ylabel('PM2.5')
    plt.grid(True)
    plt.legend()

plt.tight_layout()
plt.savefig('air-quality-comparison-filters-big.png',
            dpi=180, bbox_inches='tight')
