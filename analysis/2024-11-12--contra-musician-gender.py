#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

band_genders = {}

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

        band_genders[band] = n_men, n_women, n_nonbinary

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
            n_men, n_women, n_nonbinary = band_genders[band]

            key = n_women + n_nonbinary, n_men
            total_bookings += count
            if n_nonbinary:
                total_non_binary_bookings += count
            
            bookings_now[key] += count

print("non-binary: %.1f (%s/%s)" % (
    100 * total_non_binary_bookings / total_bookings,
    total_non_binary_bookings, total_bookings))
            
bookings_then = Counter()
# https://docs.google.com/spreadsheets/d/1fQq7pTtNVMYVRgOPbjNz2jnyw4RABGrQoplrSQntbn8/edit?gid=724157817#gid=724157817
with open("2014-2017--bookings.tsv") as inf:
    for line in inf:
        n, n_women, n_men = [int(x) for x in line.rstrip("\n").split("\t")]
        key = n_women, n_men
        bookings_then[key] += n        

total_bookings_then = sum(bookings_then.values())
total_bookings_now = sum(bookings_now.values())

MAX_MEN = 5
MAX_NON_MEN = 4

fig, axs = plt.subplots(MAX_NON_MEN, MAX_MEN, 
                        figsize=(MAX_MEN*2, MAX_NON_MEN*2))
fig.suptitle(
    'Contra Musician Bookings by Gender\n'
    'Weekends, Festivals, Camps, etc')

# Add a legend at the top of the figure
legend_ax = fig.add_axes([0.2, 0.95, 0.6, 0.02])
legend_ax.axis('off')
legend_ax.bar(0, 0, color='skyblue', label='2014-2017')
legend_ax.bar(0, 0, color='lightcoral', label='2023-2024')
legend_ax.legend(loc='center', ncol=2, bbox_to_anchor=(0.5, -2))

# Plot bars in each subplot
bar_width = 0.35

for i in range(MAX_NON_MEN):
    for j in range(MAX_MEN):
        ax = axs[MAX_NON_MEN-i-1][j]
        
        key = (i, j)
        booking_then_pct = bookings_then[key] / total_bookings_then * 100
        booking_now_pct = bookings_now[key] / total_bookings_now * 100
        
        ax.bar([0], [booking_then_pct], bar_width, color='skyblue')
        ax.bar([bar_width], [booking_now_pct], bar_width, color='lightcoral')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(0, max(25, np.ceil(max(booking_then_pct, booking_now_pct))))
        
        # Only show percentage if it's non-zero
        if booking_then_pct > 0:
            ax.text(0, booking_then_pct,
                    f'{booking_then_pct:.0f}%', ha='center', va='bottom')
        if booking_now_pct > 0:
            ax.text(bar_width, booking_now_pct,
                    f'{booking_now_pct:.0f}%', ha='center',
                    va='bottom')
        
        # Add grid labels on left and bottom edges
        if j == 0:
            ax.set_ylabel(f'{i} non-men')
        if i == 0:
            ax.set_xlabel(f'{j} men')


plt.tight_layout()
fig.savefig("contra-musician-gender-across-years-big.png", dpi=180)
plt.clf()
