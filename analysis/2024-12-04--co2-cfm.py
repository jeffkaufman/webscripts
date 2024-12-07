#!/usr/bin/env python3

import numpy as np

# Increase to cover people on stage; the last one was an open band
attendance = [171 + 5, 214 + 5, 174 + 5, 180 + 5, 177 + 5, 74 + 15]
peak_co2 = [1400, 2200, 2100, 1100, 2000, 900]

# Calculate correlation and linear regression
correlation = np.corrcoef(attendance, peak_co2)[0, 1]
slope, intercept = np.polyfit(attendance, peak_co2, 1)
print(slope, intercept)
