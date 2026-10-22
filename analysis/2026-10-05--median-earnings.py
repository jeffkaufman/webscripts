#!/usr/bin/env python3
"""
Chart the median real earnings of Americans aged 25-54, counting people with
no earnings as $0, from an IPUMS CPS ASEC extract.

Requires only matplotlib (everything else is the Python standard library).

Usage:
    python3 median_earnings_chart.py [-v] [--base-year YEAR] cps_00001_dat.gz

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
  4. Convert to dollars of --base-year (default: the latest year with both
     earnings and PCE data) using the annual average of the PCE price index
     (FRED series PCEPI).

Output: median_earnings_simple.png
"""

import argparse
import csv
import gzip
import io
import logging
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

log = logging.getLogger(__name__)

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
            log.debug("Reading %s as CSV", path)
            for row in csv.DictReader(f):
                yield {k: num(v) for k, v in row.items()}
        else:
            spans, pos = {}, 0
            for name, width in LAYOUT:
                spans[name] = (pos, pos + width)
                pos += width
            log.debug("Reading %s as fixed-width, %d chars/line: %s",
                      path, pos, spans)
            for line in f:
                yield {k: num(line[a:b]) for k, (a, b) in spans.items()}


def earnings_by_year(path):
    """Return {survey_year: [(earnings, weight), ...]}.

    There is one pair per sampled person who passes the filters: roughly
    25k-95k per year, depending on the survey's sample size. These are
    individual responses, not bins, though many people report round numbers.
    earnings is that person's total nominal earnings for the calendar year
    before the survey year. weight is ASECWT, the number of people in the
    population this respondent represents. IPUMS stores it with 4 implied
    decimals, so the raw values here are 10,000x too large, which doesn't
    change a weighted median.
    """
    data = defaultdict(list)
    dropped = defaultdict(lambda: defaultdict(int))
    for r in read_records(path):
        year = int(r["YEAR"])
        if not 25 <= r["AGE"] <= 54 or not r["ASECWT"]:
            dropped[year]["age or no weight"] += 1
            continue
        if r.get("ASECFLAG") == 2:
            dropped[year]["March basic monthly"] += 1
            continue
        if year == 2014 and r.get("HFLAG") != 1:
            dropped[year]["2014 old income questions"] += 1
            continue
        parts = [r["INCWAGE"], r["INCBUS"], r["INCFARM"]]
        # Census imputes missing income, so this is rare: under 0.1% of rows
        # in any year we chart. Treating a missing part as $0 would bias the
        # median down; dropping the person assumes they're like everyone else.
        if MISSING in parts:
            dropped[year]["missing income"] += 1
            continue
        earnings = sum(0 if p == NIU else p for p in parts)
        data[year].append((earnings, r["ASECWT"]))
    for year in sorted(set(data) | set(dropped)):
        log.debug("%d: kept %d, dropped %s", year, len(data[year]),
                  dict(dropped[year]))
    return data


def weighted_median(pairs):
    """Return the value at which cumulative weight first reaches half.

    pairs is a list of (value, weight) tuples in any order, as produced by
    earnings_by_year(). It is sorted in place. The result is always one of
    the input values, without interpolation.
    """
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
    log.debug("Fetched %d PCE rows from %s", len(rows), PCE_URL)
    for date, value in rows:
        if value:
            by_year[int(date[:4])].append(float(value))
    pce = {y: sum(v) / 12 for y, v in by_year.items() if len(v) == 12}
    log.debug("PCE has complete years %d-%d", min(pce), max(pce))
    return pce


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("path", help="IPUMS CPS extract (.dat[.gz] or .csv[.gz])")
    parser.add_argument("--base-year", type=int,
                        help="express dollars in this year's prices "
                             "(default: latest year with data)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="log debug output to stderr")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")

    data = earnings_by_year(args.path)
    pce = annual_pce()

    # Earnings refer to the calendar year before the survey.
    medians = {year - 1: weighted_median(pairs) for year, pairs in data.items()}
    for y in sorted(medians):
        log.debug("Earnings year %d: nominal median $%s", y, f"{medians[y]:,.0f}")
    base = args.base_year or max(y for y in medians if y in pce)
    if base not in pce:
        parser.error(f"no complete year of PCE data for {base}")
    log.debug("Expressing in %d dollars (PCE %.3f)", base, pce[base])
    years = sorted(y for y in medians if y >= FIRST_YEAR and y in pce)
    skipped = sorted(y for y in medians if y >= FIRST_YEAR and y not in pce)
    if skipped:
        log.debug("Skipping earnings years with no complete PCE year: %s",
                  skipped)
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
