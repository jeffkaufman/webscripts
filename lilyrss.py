#!/usr/bin/python3

from glob import glob
import os
import re
import datetime
import html

posts = []

for fname in glob(os.path.expanduser("~/lw/*.html")):
  with open(fname) as inf:
    contents = inf.read()
    if "<div id=blogpost>" in contents:
      title, = re.findall("<h1>([^<]*)</h1>", contents)
      date, = re.findall("<h2 id=date>([^<]*)</h2>", contents)

      post = contents[
        contents.index("<div id=blogpost>") + len("<div id=blogpost>"):
        contents.index("</div>")]

      post = post.replace('="/', '="https://www.lilywise.com/')
      post = post.replace("='/", "='https://www.lilywise.com/")

      short_fname = fname.split("/")[-1].replace(".html", "")
      posts.append((date, short_fname, title, post))

index = []
for date, short_fname, title, post in reversed(sorted(posts)):
  index.append('<li><a href="/%s">%s</a>' % (short_fname, title))

index_fname = os.path.expanduser("~/lw/index.html")
index_start_comment = "<!--BEGIN AUTOMATIC INDEX-->\n"
index_end_comment = "<!--END AUTOMATIC INDEX-->"
with open(index_fname) as inf:
  index_html = inf.read()
with open(index_fname, "w") as outf:
  outf.write(index_html[:index_html.find(index_start_comment) +
                        len(index_start_comment)])
  for line in index:
    outf.write(line + "\n")
  outf.write(index_html[index_html.find(index_end_comment):])

with open(os.path.expanduser("~/lw/posts.rss"), "w") as outf:
  outf.write("""<?xml version="1.0" encoding="ISO-8859-1" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">

  <channel>
    <atom:link href="https://www.lilywise.com/posts.rss" rel="self" type="application/rss+xml" />
    <title>Lily Wise's Blog Posts</title>
    <link>https://www.lilywise.com/</link>
    <description>Lily Wise's Blog Posts</description>
    <language>en-us</language>
""")
  for date, short_fname, title, post in reversed(sorted(posts)):
    post = html.escape(post)

    year, numeric_month, day = date.split('-')
    pub_date = datetime.date(
      int(year), int(numeric_month), int(day)).strftime('%d %b %Y')

    outf.write("""
<item>
  <guid>https://www.lilywise.com/%s</guid>
  <title>%s</title>
  <link>https://www.lilywise.com/%s</link>
  <pubDate>%s 08:00:00 EST</pubDate>
  <description>
  %s
  </description>
</item>""" % (short_fname, title, short_fname, pub_date, post))
  outf.write("""
</channel>
</rss>
""")
