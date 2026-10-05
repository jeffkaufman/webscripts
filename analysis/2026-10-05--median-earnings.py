#!/usr/bin/env python3
"""
Chart the median real earnings of Americans aged 25-54, counting people with
no earnings as $0, from an IPUMS CPS ASEC extract.

Requires only matplotlib (everything else is the Python standard library).

Usage:
    python3 median_earnings_chart.py cps_00001_dat.gz

Input: an IPUMS CPS extract of ASEC samples, either fixed-width (.dat or
.dat.gz) with the variable layout below, or CSV (.csv or .csv.gz), with:
    YEAR, ASECFLAG, HFLAG, ASECWT, AGE, INCWAGE, INCBUS, INCFARM

Method, per survey year:
  1. Keep people aged 25-54. Drop March basic monthly records (ASECFLAG 2).
     For 2014, keep only the subsample with the redesigned income questions
     (HFLAG 1).
  2. Earnings = wages + non-farm business income + farm income for the
     prior calendar year. "Not in universe" counts as $0.
  3. Take the median weighted by ASECWT.
  4. Convert to dollars of the latest year using the annual average of the
     PCE price index (FRED series PCEPI).

Output: median_earnings_simple.png
"""

import csv
import gzip
import io
import sys
import urllib.request
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

NIU = 99999999
MISSING = 99999998
FIRST_YEAR = 1963  # 1962-63 ASEC files show ~50% zero earners; not usable
PCE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCEPI"

# Fixed-width layout of the extract (name, width), in IPUMS column order.
# A different variable selection has a different layout: check the extract's
# codebook (.xml or .cbk) if you change it.
LAYOUT = [("YEAR", 4), ("SERIAL", 5), ("MONTH", 2), ("CPSID", 14),
          ("ASECFLAG", 1), ("HFLAG", 1), ("ASECWTH", 11), ("PERNUM", 2),
          ("CPSIDP", 14), ("CPSIDV", 15), ("ASECWT", 11), ("AGE", 2),
          ("INCWAGE", 8), ("INCBUS", 8), ("INCFARM", 8)]


def num(s):
    s = s.strip()
    return float(s) if s else None


def read_records(path):
    """Yield dicts of the variables we need, as numbers (None if blank)."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        if ".csv" in path:
            for row in csv.DictReader(f):
                yield {k: num(v) for k, v in row.items()}
        else:
            spans, pos = {}, 0
            for name, width in LAYOUT:
                spans[name] = (pos, pos + width)
                pos += width
            for line in f:
                yield {k: num(line[a:b]) for k, (a, b) in spans.items()}


def earnings_by_year(path):
    """Return {survey_year: [(earnings, weight), ...]}."""
    data = defaultdict(list)
    for r in read_records(path):
        year = int(r["YEAR"])
        if not 25 <= r["AGE"] <= 54 or not r["ASECWT"]:
            continue
        if r.get("ASECFLAG") == 2:
            continue
        if year == 2014 and r.get("HFLAG") != 1:
            continue
        parts = [r["INCWAGE"], r["INCBUS"], r["INCFARM"]]
        if MISSING in parts:
            continue
        earnings = sum(0 if p == NIU else p for p in parts)
        data[year].append((earnings, r["ASECWT"]))
    return data


def weighted_median(pairs):
    pairs.sort()
    half = sum(w for _, w in pairs) / 2
    total = 0
    for value, weight in pairs:
        total += weight
        if total >= half:
            return value


def annual_pce():
    """Return {year: average PCEPI} for complete calendar years."""
    with urllib.request.urlopen(PCE_URL) as resp:
        rows = list(csv.reader(io.TextIOWrapper(resp, "utf-8")))[1:]
    by_year = defaultdict(list)
    for date, value in rows:
        if value:
            by_year[int(date[:4])].append(float(value))
    return {y: sum(v) / 12 for y, v in by_year.items() if len(v) == 12}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = earnings_by_year(sys.argv[1])
    pce = annual_pce()

    # Earnings refer to the calendar year before the survey.
    medians = {year - 1: weighted_median(pairs) for year, pairs in data.items()}
    base = max(y for y in medians if y in pce)
    years = sorted(y for y in medians if y >= FIRST_YEAR and y in pce)
    real = [medians[y] * pce[base] / pce[y] for y in years]

    for y, v in zip(years, real):
        print(f"{y}  ${v:,.0f}")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(years, real, "o-", markersize=4)
    fig.suptitle("Median Earnings of Americans, ages 25-54", fontsize=15, y=0.97)
    ax.set_title("CPS ASEC", fontsize=11, color="#555555")
    ax.set_ylabel(f"Median Annual Earnings ({base} dollars)")
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    ax.set_ylim(0, None)
    ax.grid(alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig("median_earnings_simple.png", dpi=150)
    print("Wrote median_earnings_simple.png")


if __name__ == "__main__":
    main()
