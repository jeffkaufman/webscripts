#!/usr/bin/env python3

import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import savgol_filter


with open("attendance.json") as inf:
    attendance = json.load(inf)

covid_break_ts = 1609480992;
def spansCovidBreak(d1, d2):
    return (d1 < covid_break_ts and d2 > covid_break_ts) or (
            d1 > covid_break_ts and d2 < covid_break_ts)

def mean_absolute_percentage_error(actual, predicted):
    """Calculate MAPE, handling zero values appropriately"""
    # Filter out pairs where actual is zero to avoid division by zero
    actual = np.array(actual)
    predicted = np.array(predicted)
    non_zero = actual != 0
    if not any(non_zero):
        return 0
    return np.mean(np.abs((actual[non_zero] - predicted[non_zero]) /
    actual[non_zero])) * 100

def average_at(i):
    width = 7
    n = 0
    s = 0
    j = max(0, i - width)
    while j < min(len(attendance), i + width):
        weight = width - abs(j - i)
        if spansCovidBreak(attendance[i][0], attendance[j][0]):
            weight = 0
        n += weight
        s += weight*attendance[j][1]
        j += 1
    return s/n

for i in range(len(attendance)):
    attendance[i].append(average_at(i))

# Organize data by season
seasonal_data = defaultdict(list)
for timestamp, count, mavg in attendance:
    date = datetime.fromtimestamp(timestamp)
    # Calculate season year (the year the season starts in)
    season_year = date.year if date.month >= 8 else date.year - 1

    # Calculate days since start of season (Aug 1)
    if date.month >= 8:
        days_into_season = (date - datetime(date.year, 8, 1)).days
    else:
        days_into_season = (date - datetime(date.year - 1, 8, 1)).days

    seasonal_data[season_year].append((days_into_season, count, mavg))

# Set up the plot
plt.figure(figsize=(15, 8))

# Color map for different seasons
colors = plt.cm.viridis(np.linspace(0, 1, len(seasonal_data)))

# Plot each season
for (year, data), color in zip(sorted(seasonal_data.items()), colors):
    # Sort by day of season
    sorted_data = sorted(data)
    days = [x[0] for x in sorted_data]
    counts = [x[1] for x in sorted_data]
    mavgs = [x[2] for x in sorted_data]

    # Calculate MAPE for this season
    mape = mean_absolute_percentage_error(counts, mavgs)

    typical = np.mean(mavgs)
    adjusted = [ 100 * (x - typical) / typical
                 for x in mavgs ]

    
    plt.plot(days, adjusted,
            label=f'{year}-{year+1}',
            color=color, linewidth=2)

# Customize the plot
plt.xlabel('Month')
plt.ylabel('Number of Dancers')
plt.title('Dance Attendance Patterns by Season (with Moving Average)')

# Set x-axis ticks to months
month_positions = [0, 31, 62, 92, 123, 153, 184, 214, 245, 275, 306, 334]
month_names = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan',
               'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
plt.xticks(month_positions, month_names)

# Add grid for better readability
plt.grid(True, linestyle='--', alpha=0.3)

# Add legend in a good position
plt.legend(title='Season', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout to prevent label clipping
plt.tight_layout()

# Show the plot
plt.savefig("bida-attendance-seasonal-adjusted-big.png", dpi=180)
