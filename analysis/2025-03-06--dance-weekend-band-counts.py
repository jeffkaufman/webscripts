#!/usr/bin/env python3

import os
import json
import numpy as np
from collections import Counter

with open(os.path.expanduser("~/code/trycontra/events.json")) as inf:
    events = json.load(inf)

def mean(s):
    return sum(s) / len(s)

# from claude
def gini_coefficient(counts):
    counts_sorted = sorted(counts.values())
    n = len(counts_sorted)
        
    cumulative_sum = np.cumsum(counts_sorted)
    total = cumulative_sum[-1]
    
    # Calculate Gini coefficient using the formula
    cumulative_proportion = cumulative_sum / total
    return 1 - (2 / n) * (
        n - sum(i * counts_sorted[i] for i in range(n)) / total)

# from claude
def hhi_index(counts):
    """Calculate the Herfindahl-Hirschman Index from a Counter object"""
    total = sum(counts.values())
    
    # Calculate market shares and sum their squares
    market_shares = [(count / total) * 100 for count in counts.values()]
    return sum(share ** 2 for share in market_shares)

for event in events:
    for ignore in [
            "unnamed band", "unnnamed", "various", "lots", "open band"]:
        if ignore in event["bands"]:
            event["bands"].pop(event["bands"].index(ignore))

    for ignore in [
            "lots", "not listed", "open calling", "unnamed", "various", "TBD"]:
        if ignore in event["callers"]:
            event["callers"].pop(event["callers"].index(ignore))


print(
    "year",
    "median band bookings",
    "maximum band bookings",
    "total band bookings",
    "number of bands covering 50%",
    "band gini",
    "band hhi",
    "median caller bookings",
    "maximum caller bookings",
    "total caller bookings",
    "number of callers covering 50%",
    "caller gini",
    "caller hhi",
    sep="\t")

for year in set(event["year"] for event in events):
    if year >= 2025:
        continue

    band_counts = Counter()
    caller_counts = Counter()

    for event in events:
        if event["year"] != year:
            continue

        for band in event["bands"]:
            band_counts[band] += 1

        for caller in event["callers"]:
            caller_counts[caller] += 1

    band_observations_by_event = []
    caller_observations_by_event = []

    for event in events:
        if event["year"] != year:
            continue

        for band in event["bands"]:
            band_observations_by_event.append(band_counts[band])

        for caller in event["callers"]:
            caller_observations_by_event.append(caller_counts[caller])

    band_observations_by_event.sort()
    caller_observations_by_event.sort()

    n_bands_to_get_half = 0
    n_played_by_half = 0
    for band_count in sorted(band_counts.values(), reverse=True):
        n_bands_to_get_half += 1
        n_played_by_half += band_count
        if band_count > sum(band_counts.values()) / 2:
            break
   
    n_callers_to_get_half = 0
    n_played_by_half = 0
    for caller_count in sorted(caller_counts.values(), reverse=True):
        n_callers_to_get_half += 1
        n_played_by_half += caller_count
        if caller_count > sum(caller_counts.values()) / 2:
            break
   
    print(year,
          band_observations_by_event[len(band_observations_by_event) // 2],
          max(band_observations_by_event),
          sum(band_counts.values()),
          n_bands_to_get_half,
          gini_coefficient(band_counts),
          hhi_index(band_counts),
          caller_observations_by_event[len(caller_observations_by_event) // 2],
          max(caller_observations_by_event),
          sum(caller_counts.values()),
          n_callers_to_get_half,
          gini_coefficient(caller_counts),
          hhi_index(caller_counts),
          sep="\t"
          )
