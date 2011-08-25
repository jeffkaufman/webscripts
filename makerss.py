"""
usage:

  python makerss.py

"""

import sys, os, re
from collections import defaultdict
SITE_URL="http://sccs.swarthmore.edu/~cbr"
SITE_DIR="/home/08/cbr/public_html"
IN_HTML="%s/news_raw.html" % SITE_DIR
FRONT_PAGE="%s/index.html" % SITE_DIR
FRONT_PAGE_TMP=FRONT_PAGE+"~"
OUT_DIR="%s/news" % SITE_DIR
URL_DIR="%s/news" % SITE_URL
RSS_URL="%s/news.rss" % SITE_URL
RSS_FNAME="%s/news.rss" % SITE_DIR
RSS_MAX = 30
FRONT_PAGE_MAX=7 # how many to show on the front page
NEWS_MAIN_MAX=10 # how many to show on news/
COMMENTS_URL="http://cfebbea5.dotcloud.com/comments"
#COMMENTS_URL="http://localhost:8010/comments"


def edit_front_page(front_page_list):
  outf = open(FRONT_PAGE_TMP, "w")
  inf = open(FRONT_PAGE, "r")

  skipping = False
  for line in inf:
    if "<!-- end recent thoughts -->" in line:
      outf.write('<h3>News <small>(<a href="%s">more</a>)</small></h3>\n' % URL_DIR)
      outf.write('<table border="0" title="links to news">\n')
      outf.writelines(front_page_list)
      outf.write('</table>\n')
      skipping = False

    if not skipping:
      outf.write(line)

    if "<!-- begin recent thoughts -->" in line:
      skipping = True

  assert not skipping

  outf.close()
  inf.close()

  os.rename(FRONT_PAGE_TMP, FRONT_PAGE)
    


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
  w("    <link>%s</link>" % URL_DIR)
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
    p.write('  <a href="%s">News as rss</a><br>\n' % RSS_URL)
    p.write('  <a href="%s">Main page</a>\n' % SITE_URL)
    p.write('  </body></html>\n')


def start():
  clear_news()

  write_header()

  news_index = open(os.path.join(OUT_DIR, "index.html"), "w")
  news_index.write("<html>\n")
  news_index.write("  <head><title>Jeff :: News :: Recent</title>\n")
  news_index.write('    <link rel="alternate" type="application/rss+xml"\n')
  news_index.write('          title="RSS" href="%s">\n' % RSS_URL)
  news_index.write("  </head>\n")
  news_index.write("  <body><h2>Recent News</h2>\n")
  
  tag_to_items = defaultdict(list)

  front_page_list = []

  for n, (link_anchor, date, title, text, tags) \
        in enumerate(items(open(IN_HTML))):

    link = "%s/%s.html" % (URL_DIR, link_anchor)

    fb_tag = None
    gp_tag = None

    for tag in tags:
      for starter in ["fb/note/", "fb/status/", "g+/"]:
        if tag.startswith(starter):
          if tag.startswith('fb/'):
            fb_tag = tag
          else:
            gp_tag = tag

    if fb_tag:
      tags.remove(fb_tag)
      fb_tag = fb_tag.replace("fb/", "")

    if gp_tag:
      tags.remove(gp_tag)
      gp_tag = gp_tag.replace("g+/", "")

    if tags:
      tag_markup = ", ".join(
        '<a href="%s/%s.html">%s</a>' % (URL_DIR, tag, tag)
        for tag in tags)
      text = '<p>%s\n<div align="right"><i>\n%s<br>%s\n</i></div>\n' % (
        text, date, tag_markup)

    #guid = "%s#%s" % (URL, link_anchor)
    guid=link

    if n < RSS_MAX:
      w('    <item>')
      w('      <guid>%s</guid>' % guid)
      w("      <title>%s</title>" % title)
      w("      <link>%s</link>" % link)

    month, day, year = date.split()[1:4]

    if n < RSS_MAX:
      w("      <pubDate>%s %s %s 08:00:00 EST</pubDate>" % (day, month[:3], year))
      w("      <description>%s</description>" %
        text.replace("&", "&amp;").replace("<","&lt;").replace(">", "&gt;"))
      w("    </item>")    

    title_and_body = '<h3><a href="%s">%s</a></h3>%s\n' % (link, title, text)

    per_file = open(os.path.join(OUT_DIR, link_anchor + ".html"), "w")
    per_file.write("<html>\n")
    per_file.write("  <head><title>%s</title></head>\n" % title)
    per_file.write("  <body>%s" % title_and_body)

    if fb_tag:
      comments_full_url = "%s/%s" % (COMMENTS_URL, fb_tag)
      if gp_tag:
        comments_full_url += "/" + gp_tag
      per_file.write('<script src="%s"></script>' % comments_full_url)

    write_links_footer(per_file)
    per_file.close()

    if n < NEWS_MAIN_MAX:
      news_index.write(title_and_body)
    if n < FRONT_PAGE_MAX:
      front_page_list.append('   <tr><td>%s<td>%s<td>%s<td><a href="%s">%s</a></tr>\n' % (
        year, month, day, link, title))

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
        
  edit_front_page(front_page_list)

if __name__ == "__main__":
  start()
