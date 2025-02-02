#!/usr/bin/env python3

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from collections import defaultdict

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


            if colvalue == "0":
                colvalue = "1"

            data[colname].append(int(colvalue))

OFFSET=3

def get_post_peak_subset(test_condition, test_points):
    # Find post-peak subset using last occurrence of peak
    peak_value = max(test_points)

    peak_idx = len(test_points) - 1 - test_points[::-1].index(peak_value)

    if test_condition == 'no purifiers':
        peak_idx += 4
    elif test_condition == 'window':
        peak_idx += 6
    elif test_condition == 'vent':
        peak_idx += 3


    post_peak_subset = test_points[peak_idx + OFFSET:]
    
    while post_peak_subset[-1] < 50:
        del post_peak_subset[-1]

    post_peak_time = np.arange(len(post_peak_subset))

    return peak_idx + OFFSET, post_peak_subset, post_peak_time


condition_names = {
    'no purifiers': "Control",
}

for is_log in [True, False]:
  fig, ax = plt.subplots(figsize=(6, 6))

  for idx, test_condition in enumerate(condition_names, 1):
    test_points = data[test_condition]

    while test_points[2] < 20:
        del test_points[0]


    # Create time array starting from 0
    time = np.arange(len(test_points))

    peak_offset_idx, post_peak_subset, post_peak_time = get_post_peak_subset(
        test_condition, test_points)

    # Fit exponential decay to post-peak data


    if True:
        # Take log of concentration for linear fit
        log_concentration = np.log(post_peak_subset)
        
        # Perform linear regression in log space
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            post_peak_time, log_concentration)
        
        # Calculate decay rate (k) and initial concentration (A)
        k = -slope
        A = np.exp(intercept)
        
        # Calculate half-life
        half_life = np.log(2) / k
        
        # Calculate R-squared
        r_squared = r_value**2
        
        # Create subplot in a 2-column grid
        rows = (len(data) + 1) // 2  # Ceiling division to handle odd numbers
        plt.subplot(1,1, idx)
        
        # Plot original data
        plt.scatter(time, test_points, label='Original Data', alpha=0.5)
        
        # Plot fitted curve
        fit_time = np.linspace(0, len(post_peak_subset), 100)
        fitted_curve = A * np.exp(-k * fit_time)
        #plt.plot(fit_time + peak_offset_idx, fitted_curve,
        #        'r-', label='Fitted Decay')
    plt.ylim(ymin=10, ymax=900)
    plt.xlim(xmin=0, xmax=80)

    plt.title("PM2.5 Decay Over Time")
    fig.supxlabel('Time (minutes)')
    fig.supylabel('PM2.5 (ug/m3)')
    plt.grid(True)

    if is_log:
        plt.yscale('log')
  plt.tight_layout()
  plt.savefig('air-quality-comparison-filters-control-%sbig.png' % (
      "log-" if is_log else ""),
              dpi=180, bbox_inches='tight')
  plt.clf()
