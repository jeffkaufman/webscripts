#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

band_size = {}

# https://docs.google.com/spreadsheets/d/1fQq7pTtNVMYVRgOPbjNz2jnyw4RABGrQoplrSQntbn8/edit?gid=1118272285#gid=1118272285
with open("gender.tsv") as inf:
    for line in inf:
        if not line.strip():
            continue
        row = line.rstrip("\n").split("\t")
        if not row[0]:
            continue

        band, n_men, n_women, n_nonbinary = row
        n_men = int(n_men or "0")
        n_women = int(n_women or "0")
        n_nonbinary = int(n_nonbinary or "0")

        band_size[band] = n_men + n_women + n_nonbinary

total_bookings = 0
total_non_binary_bookings = 0
bookings_now = Counter()
for year in "2023", "2024":
    with open("%s.tsv" % year) as inf:
        for line in inf:
            if not line.strip():
                continue
            band, count = line.rstrip("\n").split("\t")
            count = int(count)

            bookings_now[band_size[band]] += count

bookings_then = Counter()
# https://docs.google.com/spreadsheets/d/1fQq7pTtNVMYVRgOPbjNz2jnyw4RABGrQoplrSQntbn8/edit?gid=724157817#gid=724157817
with open("2014-2017--bookings.tsv") as inf:
    for line in inf:
        n, n_women, n_men = [int(x) for x in line.rstrip("\n").split("\t")]
        size = n_women + n_men
        bookings_then[size] += n

total_bookings_then = sum(bookings_then.values())
total_bookings_now = sum(bookings_now.values())

xs = []
ys_then = []
ys_now = []
for size in range(1,6):
    print("%s: %.1f%% -> %.1f%%" % (
        size,
        bookings_then[size] / total_bookings_then * 100,
        bookings_now[size] / total_bookings_now * 100,
    ))
    xs.append(size)
    ys_then.append(bookings_then[size] / total_bookings_then * 100)
    ys_now.append(bookings_now[size] / total_bookings_now * 100)

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

fig, ax = plt.subplots()
ax.set_xticks([1,2,3,4,5])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.plot(xs, ys_then, label="2014-2027")
ax.plot(xs, ys_now, label="2023-2024")
ax.set_title("Band Size Distribution\nWeekends, Festivals, etc")
fig.savefig("band-sizes.png", dpi=180)
plt.clf()

print("Average 2014-2017: %.3f" % (np.average(xs, weights=ys_then)))
print("Average 2023-2024: %.3f" % (np.average(xs, weights=ys_now)))
