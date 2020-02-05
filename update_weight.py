#!/usr/bin/env python3
import time

print("Visit https://keep.google.com/#NOTE/13EE8d0JDw6I5JYDg5TllygRlSG1sNdb61xlITNtQwfynFKuivOu-PybF4jOL1oIacyE8Gg")
print("and paste contents; press Ctrl-C when done.")

lines = []
try:
  while True:
    lines.append(input())
except KeyboardInterrupt:
  pass

def to_epoch(year, month, day):
  return int(time.mktime(time.strptime('%s-%s-%s' % (
    year, month, day), '%Y-%m-%d')))  

year = 2017
prev = 0
vals = []
for line in lines:
  if not line.strip():
    continue
  date, weight = line.strip().split()
  weight = float(weight)
  month, day = date.split('/')
  month, day = int(month), int(day)

  cur = to_epoch(year, month, day)
  if cur < prev:
    year += 1
    cur = to_epoch(year, month, day)

  vals.append((cur, weight))
  prev = cur

import json
with open('/home/jefftk/jtk/weight.log', 'w') as outf:
  outf.write(json.dumps(vals))
