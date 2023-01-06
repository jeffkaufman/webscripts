#!/usr/bin/python3

from glob import glob
import os
import re
import datetime
import html
import sys

# Usage: ./kidrss.py <lily|anna>
user, = sys.argv[1:]

config = {
  "lily": {
    "path": "lw",
    "domain": "lilywise.com",
    "name": "Lily Wise",
  },
  "anna": {
    "path": "aw",
    "domain": "annawise.net",
    "name": "Anna Wise",
  },
}[user]

posts = []

indir = os.path.join(os.path.expanduser("~"), config["path"])

for fname in glob(os.path.join(indir, "*.html")):
  with open(fname) as inf:
    contents = inf.read()
    if "<div id=blogpost>" in contents:
      title, = re.findall("<h1>(?:<span>)?([^<]*)(?:</span>)?</h1>", contents)
      date, = re.findall("<h2 id=date>(?:<span>)?([^<]*)(?:</span>)?</h2>",
                         contents)

      post = contents[
        contents.index("<div id=blogpost>") + len("<div id=blogpost>"):
        contents.index("</div>")]

      post = post.replace('="/', '="https://www.' + config["domain"] + '/')
      post = post.replace("='/", "='https://www." + config["domain"] + "/")

      short_fname = fname.split("/")[-1].replace(".html", "")
      posts.append((date, short_fname, title, post))

index = []
for date, short_fname, title, post in reversed(sorted(posts)):
  index.append('<li><a href="/%s">%s</a>' % (short_fname, title))

index_fname = os.path.join(indir, "index.html")
index_start_comment = "<!--BEGIN AUTOMATIC INDEX-->\n"
index_end_comment = "<!--END AUTOMATIC INDEX-->"
with open(index_fname) as inf:
  index_html = inf.read()

if index_start_comment not in index_html:
  raise Exception("missing index_start_comment")
if index_end_comment not in index_html:
  raise Exception("missing index_end_comment")

with open(index_fname, "w") as outf:
  outf.write(index_html[:index_html.find(index_start_comment) +
                        len(index_start_comment)])
  for line in index:
    outf.write(line + "\n")
  outf.write(index_html[index_html.find(index_end_comment):])

with open(os.path.join(indir, "posts.rss"), "w") as outf:
  outf.write("""<?xml version="1.0" encoding="ISO-8859-1" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">

  <channel>
    <atom:link href="https://www.%s/posts.rss" rel="self" type="application/rss+xml" />
    <title>%s's Blog Posts</title>
    <link>https://www.%s/</link>
    <description>%s's Blog Posts</description>
    <language>en-us</language>
""" % (config['domain'], config['name'],
       config['domain'], config['name']))
  for date, short_fname, title, post in reversed(sorted(posts)):
    post = html.escape(post)

    year, numeric_month, day = date.split('-')
    pub_date = datetime.date(
      int(year), int(numeric_month), int(day)).strftime('%d %b %Y')

    outf.write("""
<item>
  <guid>https://www.%s/%s</guid>
  <title>%s</title>
  <link>https://www.%s/%s</link>
  <pubDate>%s 08:00:00 EST</pubDate>
  <description>
  %s
  </description>
</item>""" % (config['domain'], short_fname,
              title,
              config['domain'], short_fname,
              pub_date,
              post))
  outf.write("""
</channel>
</rss>
""")
