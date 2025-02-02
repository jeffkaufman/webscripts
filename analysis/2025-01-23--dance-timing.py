#!/usr/bin/env python3


import datetime
from collections import Counter, defaultdict

start_by_year = defaultdict(Counter)
length_by_year = defaultdict(Counter)

with open("free-raisins.tsv") as inf:
    for line in inf:
        if line.startswith("Year"):
            continue

        year, date, time, location = line.rstrip("\n").split("\t")

        month, day = date.split()

        date = "%s-%s-%s" % (
            year,
            {"Jan": "01",
             "Feb": "02",
             "Mar": "03",
             "Apr": "04",
             "May": "05",
             "Jun": "06",
             "Jul": "07",
             "Aug": "08",
             "Sep": "09",
             "Oct": "10",
             "Nov": "11",
             "Dec": "12"}[month],
            day.zfill(2))

        time = time.split(",")[-1].strip()
        time = time.split(";")[-1].strip()

        start, end = time.split("-")

        if ":" not in start:
            start = start + ":00"
        if ":" not in end:
            end = end + ":00"

        start_t = datetime.datetime.strptime(start, "%H:%M")
        end_t = datetime.datetime.strptime(end, "%H:%M")

        length = end_t - start_t
            
        #print(start, date, start, end, length, location, sep="\t")
        
        start_by_year[year][start] += 1
        length_by_year[year][length] += 1

hr3 = datetime.timedelta(hours=3, minutes=00)
print("year", "<3hr", "3hr", ">3hr", sep="\t")
for year in length_by_year:
    lt_3 = 0
    eq_3 = 0
    gt_3 = 0
    
    for length, count in length_by_year[year].items():
        if length < hr3:
            lt_3 += count
        elif length == hr3:
            eq_3 += count
        elif length > hr3:
            gt_3 += count
        else:
            assert False
    
    print(year, lt_3, eq_3, gt_3, sep="\t")

print("total",
      sum(count
          for year in length_by_year
          for length, count in length_by_year[year].items()
          if length < hr3),
      sum(count
          for year in length_by_year
          for length, count in length_by_year[year].items()
          if length == hr3),
      sum(count
          for year in length_by_year
          for length, count in length_by_year[year].items()
          if length > hr3),
      sep="\t")

print()
print()

# this wouldn't work if anything started after 9:59, but nothing does
hr8 = "8:00"
print("year", "<8pm", "8pm", ">8pm", sep="\t")
for year in start_by_year:
    lt_8 = 0
    eq_8 = 0
    gt_8 = 0
    
    for start, count in start_by_year[year].items():
        if start < hr8:
            lt_8 += count
        elif start == hr8:
            eq_8 += count
        elif start > hr8:
            gt_8 += count
        else:
            assert False
    
    print(year, lt_8, eq_8, gt_8, sep="\t")

print("total",
      sum(count
          for year in start_by_year
          for start, count in start_by_year[year].items()
          if start < hr8),
      sum(count
          for year in start_by_year
          for start, count in start_by_year[year].items()
          if start == hr8),
      sum(count
          for year in start_by_year
          for start, count in start_by_year[year].items()
          if start > hr8),
      sep="\t")

       
