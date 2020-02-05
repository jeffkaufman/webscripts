#!/usr/bin/env python3
import time

print("Visit https://docs.google.com/spreadsheets/d/1S3Xntc9OwxE1npAFwcU7FGCGdyaVbhfhXcXlMga-zAY/edit")
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

vals = []
for line in lines:
  if not line.strip():
    continue
  date_s, total_s = line.split('\t')
  if date_s == 'date':
    continue

  month, day, year = date_s.split('/')
  ts = to_epoch(year, month, day)
  vals.append((ts, int(total_s)))

import json
with open('/home/jefftk/bd/attendance.log', 'w') as outf:
  outf.write(json.dumps(vals))

print('\nWrote %s data points.' % len(vals))
