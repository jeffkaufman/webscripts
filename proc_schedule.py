""" processes the special events table in INDEX_FNAME """

import os
import sys
import re
from pprint import pprint
from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta
import calendar

INDEX_FNAME="/home/08/cbr/public_html/index.html"
CAL_FNAME="/home/08/cbr/public_html/schedule.ical"

SPECIAL_TABLE='<table border="1" title="special events" cellspacing="0" cellpadding="2">'

def parse_table(table_strings):
    def clean(s):
        if s is None:
            return s
        s=str(s)
        for f, r in [["<td>", ""],
                     ["</td>", ""],
                     ["\n", " "],
                     ["\t", " "],
                     ["  ", " "]]:
            s = s.replace(f, r)
        return s.strip()

    parse=[]
    soup = BeautifulSoup("".join(table_strings))
    for row in soup.table:
        if len(row) == 7:
            ignore, day_name, month, day_num, activity, time, location = [
                clean(x) for x in row]

            day_name = day_name.replace("Thr", "Thu")

            target_date = parse_date(month, day_num, location, day_name)
            parse.append((target_date, activity, time, location))

    return parse

def unparse_table(parse):
    lines=['    %s\n' % SPECIAL_TABLE]
    def unclean(s):
        return "<td>%s"%s

    def w(s, ind=8):
        lines.append("%s%s\n" % (" "*ind, s))
        
    for target_date, activity, time, location in parse:
        w("<tr>", ind=6)
        w(target_date.strftime("<td>%a<td>%b<td>%d").replace(
            "<td>0", "<td>").replace("<td>Thu<td>", "<td>Thr<td>"))
        w(unclean(activity))
        w(unclean(time))
        w(unclean(location))

    lines.append('    </table>\n')

    return lines

def month_number_from_abbr(month_abbr):
    if month_abbr.isdigit():
        return int(month_abbr)

    cands = [idx for idx, month in enumerate(calendar.month_abbr)
            if month.lower() == month_abbr.lower()]
    if len(cands) != 1:
        raise Exception("'%s' is not a valid month abbreviation" % (
            month_abbr))
    return cands[0]
                        

def parse_date(month, day_num, location="", day_name=None):
    year = None
    match = re.match(r".*\(([0-9]{4})\)$", location)
    if match:
        year = int(match.group(1))

    # dates up to 8 weeks ago are this year, otherwise next year
    pivot_date = date.today() - timedelta(weeks=8)

    day_num = int(day_num)
    
    month_number=month_number_from_abbr(month)

    date_this_year, date_next_year, date_then_year = None, None, None
    try:
        date_this_year = date(pivot_date.year, month_number, day_num)
    except ValueError:
        pass

    try:
        date_next_year = date(pivot_date.year + 1, month_number, day_num)
    except ValueError:
        pass

    if year is not None:
        try:
            date_then_year = date(year, month_number, day_num)
        except ValueError:
            pass


    if date_then_year is not None:
        target_date = date_then_year
    else:
        target_date = date_this_year
        year=pivot_date.year
        if date_this_year is None or date_this_year < pivot_date:
            target_date = date_next_year
            year = year + 1

    if target_date is None:
        raise Exception("The date %s/%s/%s does not appear to be valid." % (
            month_number, day_num, year))

    if day_name is not None:
        target_day_name=target_date.strftime("%a")

        if target_day_name != day_name:
            raise Exception("The date %s %s %s appears to be a %s not a %s" % (
                day_num, month, year, target_day_name, day_name))

    return target_date

def add_to_table(table_entry, table):
    new_table = []
    appended = False
    for old_entry in table:
        if not appended and old_entry[0] > table_entry[0]:
            new_table.append(table_entry)
            appended = True
        new_table.append(old_entry)
    if not appended:
        new_table.append(table_entry)
    return new_table
        

def make_table_entry(month, day_num, activity, time, location, day_name=None):
    def clean(x):
        for f, r in [["&", "&amp;"],
                     ["<", "&lt;"],
                     [">", "&gt;"]]:
            x = x.replace(f, r)
        return x

    target_date = parse_date(month, day_num, location, day_name)
        
    return target_date, clean(activity), clean(time), clean(location)

def rpad(s, amt):
    return (s+" "*amt)[:amt]

def pretty_date(d, yearfirst=True):
    if yearfirst:
        return d.strftime("%Y  %a %b %d")
    return d.strftime("%a %b %d, %Y")

def tidy_view(table_entries, ind=0, nodate=False):
    indent = " "*ind
    lines = []

    def mk_tc(target_date, time):
        if nodate:
            return indent
        return "%s%s %s  "%(indent, pretty_date(target_date),time)

    maxtime=""
    for target_date, activity, time, location in table_entries:
        tc = mk_tc(target_date, time)
        if len(tc) > len(maxtime):
            maxtime = tc
    
    for target_date, activity, time, location  in table_entries:
        time_component = rpad(mk_tc(target_date, time), len(maxtime))

        s = "%s%s (%s)" % (time_component, activity, location)
        s = re.sub("<[^>]*>","",s)
        lines.append(s)
        
    return "\n".join(lines)

def read_index(fname=INDEX_FNAME):
    inf = open(fname)

    before_table_lines = []
    table_lines = []
    after_table_lines = None # None until we're done with table
    for line in inf:
        if after_table_lines is not None:
            after_table_lines.append(line)
        elif table_lines:
            table_lines.append(line)
            if "</table>" in line:
                after_table_lines = []
        elif SPECIAL_TABLE in line:
            table_lines.append(line)
        else:
            before_table_lines.append(line)
            
    inf.close()

    return before_table_lines, table_lines, after_table_lines

def write_index(before, table, after, fname=INDEX_FNAME):
    os.rename(fname, fname + "~")
    outf = open(fname, "w")
    outf.writelines(before)
    outf.writelines(table)
    outf.writelines(after)
    outf.close()

def parse_time(time):
   """ """

   time = time.lower().strip().replace(",", " ").replace(" - ", "-").split()[0]

   if time in "*?":
     return None

   if "-" in time:
      start_time, end_time = time.split("-")
   else:
      start_time, end_time = time, time

   def clean(a_time):
      for f, r in (("ish", ""),
                   ("morning", "9am"),
                   ("afternoon", "3pm"),
                   ("evening", "7pm"),
                   ("dinner", "6pm"),
                   ("noon", "12am"),
                   ("midnight", "12pm")):
        a_time = a_time.replace(f, r)
                   

      a_time = a_time.replace("ish", "")
      
      which = None # AM, PM, None
      if "am" in a_time:
         which = "AM"
         a_time = a_time.replace("am", "")
      elif "pm" in a_time:
         which = "PM"
         a_time = a_time.replace("pm", "")

      if ":" in a_time:
         hours, minutes = a_time.split(":")
      else:
         hours, minutes = a_time, "00"

      hours, minutes = int(hours), int(minutes)

      if which == "PM" or (which is None and hours <= 9):
         hours += 12

      hours, minutes = str(hours).zfill(2), str(minutes).zfill(2)
      assert len(hours) == len(minutes) == 2 
      return hours, minutes

   return clean(start_time), clean(end_time)

def write_ical(out=CAL_FNAME):
        a,b,c = read_index(INDEX_FNAME)
    
        lines = []
        def w(s):
          lines.append(s+"\n")

        w("BEGIN:VCALENDAR")
        w("VERSION:2.0")
        w("PRODID:-//Google Inc//Google Calendar 70.9054//EN")

        for date, descr, time, location in parse_table(b):
          w("BEGIN:VEVENT")
          date_str = date.strftime("%Y%m%d")

          parsed_time = parse_time(time)
          if parsed_time:
            (start_hr, start_min), (end_hr, end_min) = parsed_time
            w("DTSTART;TZID=America/New_York:%sT%s%s00" % (
                  date_str, start_hr, start_min))
            w("DTEND;TZID=America/New_York:%sT%s%s00" % (
                  date_str, end_hr, end_min))
          else:
            w("DTSTART;DATE:%s" % date_str)
            w("DTEND;DATE:%s" % date_str)

          w("LOCATION:%s" % location)
          w("SUMMARY:%s" % descr)
          w("END:VEVENT")

        w("END:VCALENDAR")
        open(out, "w").writelines(lines)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Expected opcode.  Allowed:"
        print "  rewrite"
        print "  add"
        print "  view"
        print "  ical"
        
    elif sys.argv[1] == "ical":
        write_ical()

    elif sys.argv[1] == "rewrite":
        a,b,c = read_index(INDEX_FNAME)
    
        t=parse_table(b)
        pprint(t)
        u=unparse_table(t)
        pprint(u)
    
        write_index(a,u,c,INDEX_FNAME)
    elif sys.argv[1] == "add":
        if len(sys.argv) == 2:
            table_entry = make_table_entry(
                raw_input("month: "),
                raw_input("day_num: "),
                raw_input("activity: "),
                raw_input("time: "),
                raw_input("location: "))
        else:
            table_entry = make_table_entry(*sys.argv[2:])
        a,b,c = read_index(INDEX_FNAME)
        t=parse_table(b)     

        t = add_to_table(table_entry, t)

        print
        print "The day %s looks like:" % pretty_date(table_entry[0],yearfirst=False)
        print tidy_view([te for te in t if te[0] == table_entry[0]],
                         ind=3, nodate=True)
        write_index(a,unparse_table(t),c,INDEX_FNAME)
    elif sys.argv[1] == "view":
        a,b,c = read_index(INDEX_FNAME)
        t=parse_table(b)
        print tidy_view(parse_table(b))
    else:
        print "Args not understood: %s" % (" ".join(sys.argv[1:]))
