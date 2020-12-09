import os
import sys
import re
from pprint import pprint
import datetime
from datetime import date, timedelta
import calendar

WEBDIR="/home/jefftk/kf/"
FUTURE_FNAME="%s/index.html" % WEBDIR
CAL_FNAME="%s/schedule.ical" % WEBDIR

SPECIAL_TABLE='<table id=schedule rules=groups border=1 frame=hsides bordercolor=white>'

def strip_tags(s):
    return re.sub("<[^>]*>","",s).strip()

def to_numeric_date(date_s):
    month, day = date_s.split()
    return month_number_from_abbr(month), int(day)

def expand_days(dates, year):
    if "<br>" not in dates:
        assert "-" not in dates
        return [to_numeric_date(dates)]
    begin, end = dates.split("<br>")
    assert begin.endswith("-")
    begin = begin[:-1] # remove final -

    begin_month_n, begin_day_n = to_numeric_date(begin)
    end_month_n, end_day_n = to_numeric_date(end)

    begin_d = datetime.date(year, begin_month_n, begin_day_n)
    end_d = datetime.date(year, end_month_n, end_day_n)

    dates = []
    for i in range((end_d - begin_d).days + 1):
        intermediate_date = begin_d + timedelta(days=i)
        dates.append((intermediate_date.month, intermediate_date.day))

    return dates

def parse_table(table_strings, offset):
    events = []

    year = None
    days = None
    place = None

    state = "pre comment"
    for i, line in enumerate(table_strings):
      try:
        line = line.strip()
        if state == "pre comment":
            if line == "-->":
                state = "pre entry"
            else:
                continue
        elif state == "pre entry":
            if line == "<tr>":
                state = "need year"
            else:
                continue
        elif state == "need year":
            assert line.startswith("<td")
            assert not year
            year = int(line.replace("<td>",""))
            state = "need days"
        elif state == "need days":
            assert line.startswith("<td")
            assert not days
            days = line.replace("<td>","",1)
            state = "need place"
        elif state == "need place":
            assert line.startswith("<td")
            assert not place
            place = line.replace("<td>","",1)
            state = "maybe more place"
        elif state == "maybe more place":
            if not line.startswith("<"):
                place = "%s %s" % (place, line)
            state = "pre entry"
            for day in expand_days(days, year):
                events.append([year, day, strip_tags(place)])

            year = days = place = None
        else:
            assert False
      except Exception:
        print("On line %s" % (i+offset))
        raise

    return events

def month_number_from_abbr(month_abbr):
    if month_abbr.isdigit():
        return int(month_abbr)

    cands = [idx for idx, month in enumerate(calendar.month_abbr)
            if month.lower() == month_abbr.lower()]
    if len(cands) != 1:
        raise Exception("'%s' is not a valid month abbreviation" % (
            month_abbr))
    return cands[0]

def read_index(fname=FUTURE_FNAME):
    inf = open(fname)

    before_table_lines = []
    table_lines = []
    after_table_lines = None # None until we're done with table
    offset = None
    for i, line in enumerate(inf):
        if after_table_lines is not None:
            after_table_lines.append(line)
        elif table_lines:
            table_lines.append(line)
            if "<!-- END SCHEDULE TABLE -->" in line:
                after_table_lines = []
        elif "<!-- BEGIN SCHEDULE TABLE -->" in line:
            table_lines.append(line)
            offset = i
        else:
            before_table_lines.append(line)

    inf.close()

    return table_lines, offset

def write_ical(out=CAL_FNAME):
        lines = []
        def w(s):
          lines.append(s+"\n")

        w("BEGIN:VCALENDAR")
        w("VERSION:2.0")
        w("PRODID:-//Google Inc//Google Calendar 70.9054//EN")

        for year, (month, day), descr in parse_table(*read_index()):
          date = datetime.date(year, month, day)
          if in_past(date):
              continue

          date_str = date.strftime("%Y%m%d")

          w("BEGIN:VEVENT")
          w("DTSTART;VALUE=DATE:%s" % date_str)
          w("DTEND;VALUE=DATE:%s" % date_str)
          w("SUMMARY: kf@ %s" % descr)
          w("END:VEVENT")

        w("END:VCALENDAR")
        open(out, "w").writelines(lines)

def in_past(date):
    def dstr(x):
        return x.strftime("%Y-%m-%d")
    return dstr(datetime.datetime.now()) > dstr(date)

if __name__ == "__main__":
    write_ical()
