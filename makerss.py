"""
usage:

  python makerss.py public_html/news.html > public_html/news.rss

This is a partial rewrite to make this usable with django

"""



import sys, os, re
from collections import defaultdict
SITE_URL="http://sccs.swarthmore.edu/~cbr"
SITE_DIR="/home/08/cbr/public_html"
IN_HTML="%s/news.html" % SITE_DIR
URL="%s/news.html" % SITE_URL
OUT_DIR="%s/news" % SITE_DIR
URL_DIR="%s/news" % SITE_URL
RSS_URL="%s/news.rss" % SITE_URL
RSS_FNAME="%s/news.rss" % SITE_DIR

def clear_news():
  for x in os.listdir(OUT_DIR):
    if x.endswith(".html"):
      os.remove(os.path.join(OUT_DIR,x))

if __name__ == "__main__":
  RSS_OUT=open(RSS_FNAME, "w")
  def w(s):
    RSS_OUT.write(s + "\n")
else:
  def w(s):
    print s

def write_header():
  w('<?xml version="1.0" encoding="ISO-8859-1" ?>')
  w('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
  w('')
  w('  <channel>')
  w('    <atom:link href="%s" rel="self" type="application/rss+xml" />' % RSS_URL)
  w("    <title>Jeff :: News</title>")
  w("    <link>%s</link>" % URL)
  w("    <description>News From a Possibly No Longer Out Of Date Source</description>")
  w("    <language>en-us</language>")

def write_footer():
  w("  </channel>")
  w("</rss>")


ITEM_RE = re.compile(r'<a name="([^"]*)"></a><h3>([^:]*):</h3>')
TITLE_RE = re.compile(r'<h3>([^>]*)</h3>')
TAGS_RE = re.compile(r'<h4>Tags:([^>]*)</h4>')

def items(s):
  
  cur_item = []

  def no_title():
    return len(cur_item) == 2

  def sendout():
    if no_title():
      cur_item.append("untitled")
    cur_item.append("".join(cur_text))
    cur_item.append(set(cur_tags))
    for z in cur_text[:]:
      cur_text.remove(z)
    x = cur_item[:]
    for z in x:
      cur_item.remove(z)
    for z in cur_tags[:]:
      cur_tags.remove(z)
    return x
  
  cur_text = []
  cur_tags = []
  for line in s:
    
    match = ITEM_RE.search(line)
    if match:
      if cur_item:
        yield sendout()
      
      link_anchor, date = match.groups()
      cur_item.append(link_anchor)
      cur_item.append(date)

    elif not cur_item:
      pass
    
    else:

      if no_title():
        match = TITLE_RE.search(line)
        if match:
          cur_item.append(match.groups()[0])
          continue
      
      tags_match = TAGS_RE.search(line)
      if tags_match:
        cur_tags=[x.strip() for x in
                  tags_match.groups()[0].split(",")]
        continue

      line = line.replace('<div class="pt">', '')
      line = line.replace('<DIV CLASS="PT">', '')
      line = line.replace('</div>', '')
      if line.startswith("<hr>"):
        break
      cur_text.append(line)

  if cur_item:
    yield sendout()
      
        
def write_links_footer(p):
    p.write("  <hr>\n")
    p.write('  <a href="%s/all.html">Links to news items by date and title</a><br>\n' % URL_DIR)
    p.write('  <a href="%s/index.html">Recent news</a><br>\n' % URL_DIR)
    p.write('  <a href="%s">All news in one file</a><br>\n' % URL)
    p.write('  <a href="%s">News as rss</a><br>\n' % RSS_URL)
    p.write('  <a href="%s">Main page</a>\n' % SITE_URL)
    p.write('  </body></html>\n')


def start():
  clear_news()

  write_header()

  news_index = open(os.path.join(OUT_DIR, "index.html"), "w")
  news_index.write("<html>\n")
  news_index.write("  <head><title>Jeff :: News :: Recent</title></head>\n")
  news_index.write("  <body><h2>Recent News</h2>\n")
  
  tag_to_items = defaultdict(list)

  for n, (link_anchor, date, title, text, tags) \
        in enumerate(items(open(IN_HTML))):

    link = "%s/%s.html" % (URL_DIR, link_anchor)

    if tags:
      tag_markup = ", ".join(
        '<a href="%s/%s.html">%s</a>' % (URL_DIR, tag, tag)
        for tag in tags)
      text = '%s\n<div align="right">\n%s\n</div>\n' % (
        text, tag_markup)

    #guid = "%s#%s" % (URL, link_anchor)
    guid=link
    full_title="%s -- %s" % (date, title)
    w('    <item>')
    w('      <guid>%s</guid>' % guid)
    w("      <title>%s</title>" % full_title)
    w("      <link>%s</link>" % link)

    month, day, year = date.split()[1:4]

    w("      <pubDate>%s %s %s</pubDate>" % (day, month[:3], year))
    w("      <description>%s</description>" %
      text.replace("&", "&amp;").replace("<","&lt;").replace(">", "&gt;"))
    w("    </item>")    

    per_file = open(os.path.join(OUT_DIR, link_anchor + ".html"), "w")
    per_file.write("<html>\n")
    per_file.write("  <head><title>%s</title></head>\n" % full_title)
    per_file.write("  <body><h3>%s</h3>%s" % (full_title,text))
    write_links_footer(per_file)
    per_file.close()

    if n < 10:
      news_index.write('<h3><a href="%s">%s</a></h3>%s\n' % (
        link, full_title, text))

    tags.add("all")
    for tag in tags:
      tag_to_items[tag].append((year, month, day, link, title))


  for tag, item_list in tag_to_items.items():
    t = open(os.path.join(OUT_DIR, "%s.html" % tag), "w").write
    t("<html>\n")
    t("  <head><title>Jeff :: News :: %s</title></head>\n" % tag)
    t('  <body><h2>News :: %s</h2>\n<table border="0">\n' % tag)
    for year, month, day, link, title in item_list:
      t('   <tr><td>%s<td>%s<td>%s<td><a href="%s">%s</a></tr>\n' % (
        year, month, day, link, title))
    t('  </table>\n')
    t('  </body>\n')
    t('</html>\n')

  write_footer()
  write_links_footer(news_index)
        


if __name__ == "__main__":
  start()
