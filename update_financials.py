#!/usr/bin/env python3
import time

print("Visit https://docs.google.com/spreadsheets/d/1PvCEAlAluF5Cf0J2s_C0AaAQ4HpgjF4WT1XVpV5DcuQ/edit#gid=1315149313")
print("and make sure it's up to date.  Then paste contents here.")
print("Press Ctrl-C when done.")

lines = []
try:
  while True:
    lines.append(input())
except KeyboardInterrupt:
  pass

def parse_money(s):
  s = s.replace('$', '').replace(',', '').strip()
  if not s:
    return None
  
  return round(float(s))

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
  date_s, income_s, profit_s = line.split('\t')
  if date_s == 'date':
    continue

  year, month, day = date_s.split('-')
  ts = to_epoch(year, month, day)
  vals.append((ts, parse_money(income_s), parse_money(profit_s)))

import json
with open('/home/jefftk/bd/financials.log', 'w') as outf:
  outf.write(json.dumps(vals))

print('\nWrote %s data points.' % len(vals))
