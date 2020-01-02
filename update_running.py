#!/usr/bin/env python3
import time

print("Visit https://keep.google.com/#NOTE/161516dcdcd.aa233a1f65d807ce")
print("and paste contents; press Ctrl-C when done.")

lines = []
try:
  while True:
    lines.append(input())
except KeyboardInterrupt:
  pass

def to_epoch(year, month, day):
  try:
    return int(time.mktime(time.strptime('%s-%s-%s' % (
      year, month, day), '%Y-%m-%d')))
  except Exception:
    print((year, month, day))
    raise

year = 2018
prev = 0
vals = []
for line in lines:
  if not line.strip():
    continue
  date, duration = line.strip().split()[0:2]
  duration_m, duration_s = [int(x) for x in duration.split(':')]
  month, day = date.split('/')
  month, day = int(month), int(day)

  cur = to_epoch(year, month, day)
  if cur < prev:
    year += 1
    cur = to_epoch(year, month, day)

  vals.append((cur, (duration_s + 60*duration_m)/60))
  prev = cur

import json
with open('/home/jefftk/jtk/running.log', 'w') as outf:
  outf.write(json.dumps(vals))
