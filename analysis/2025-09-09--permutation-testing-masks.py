#!/usr/bin/env python3

import random

required_counts = [119, 142, 143, 143, 145, 158, 180, 187, 189, 201, 221]
optional_counts = [111, 121, 152, 171, 173, 176, 182, 186, 194, 208, 212, 288]

print(len(optional_counts + required_counts))

def attendance_ratio(req, opt):
    return ((sum(req) / len(req)) /
            (sum(opt) / len(opt)))

threshold = attendance_ratio(required_counts, optional_counts)

simulations = 10000000
at_least_this_extreme = 0

for _ in range(simulations):
    counts = required_counts + optional_counts
    random.shuffle(counts)
    if attendance_ratio(counts[:len(required_counts)],
                        counts[len(required_counts):]) <= threshold:
        at_least_this_extreme += 1

print(f"Out of {simulations} simulations, {at_least_this_extreme} "
      f"({100*at_least_this_extreme/simulations}%) "
      f"were at least this extreme ({threshold})")


