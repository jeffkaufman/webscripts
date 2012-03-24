"""
usage:

  python makerss.py

"""

import sys, os, re

SITE_URL="http://www.jefftk.com"
SITE_DIR="/home/jeff/jtk"
IN_HTML="%s/news_raw.html" % SITE_DIR
FRONT_PAGE="%s/index.html" % SITE_DIR
FRONT_PAGE_TMP=FRONT_PAGE+"~"
OUT_DIR="%s/news" % SITE_DIR
URL_DIR="%s/news" % SITE_URL
RSS_URL="%s/news.rss" % SITE_URL
RSS_FNAME="%s/news.rss" % SITE_DIR
RSS_MAX = 30
FRONT_PAGE_MAX=6 # how many to show on the front page
COMMENTS_URL="http://cfebbea5.dotcloud.com/comments"
#COMMENTS_URL="http://localhost:8010/comments"

GP_UID="103013777355236494008"

GA_STR = """
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-27645543-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
"""


def edit_front_page(front_page_list):
  outf = open(FRONT_PAGE_TMP, "w")
  inf = open(FRONT_PAGE, "r")

  skipping = False
  for line in inf:
    if "<!-- end recent thoughts -->" in line:
      outf.write('<table border="0" title="links to news" valign="top">\n')
      outf.write('<tr><td colspan="3"><b>Blog Posts</b><td rowspan="100">')
      outf.writelines(front_page_list[:FRONT_PAGE_MAX])
      outf.write('<tr><td><td><td><td><a href="%s">more posts...</a>\n' % URL_DIR)
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
  w("    <description>Jeff Kaufman's Blog</description>")
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


def links_partial(tag_block=""):
  sep = '&nbsp;&nbsp;::&nbsp;&nbsp;'
  s = sep.join(
    ('<a href="%s" rel="author">Jeff Kaufman</a>' % SITE_URL,
     '<a href="%s/all.html">Blog Posts</a>' % URL_DIR,
     '<a href="%s">RSS Feed</a>' % RSS_URL,
     '<a href="%s/contact.html">Contact</a>' % SITE_URL))
  if tag_block:
    s += sep + "Tagged: " + tag_block

  s += "\n"
  return s


def write_links_footer(p, tag_block):
    p.write("  <hr>\n")
    p.write(links_partial(tag_block))
    p.write('  </body></html>\n')

def start():
  clear_news()
  os.symlink("%s/all.html" % OUT_DIR, "%s/index.html" % OUT_DIR)

  write_header()

  css = ('<style type="text/css">'
         #'li, p, blockquote {max-width:35em;}'
         '.date {float: right; display: block}'
         '.content {max-width:35em;}'
         '</style>')

  tag_to_items = {}

  front_page_list = []

  for n, (link_anchor, date, title, text, tags) \
        in enumerate(items(open(IN_HTML))):

    text = re.sub(r'href="(20\d\d-\d\d?-\d\d?)"',
                  r'href="%s/\1.html"' % URL_DIR,
                  text)

    text = text.replace('href="/', 'href="%s/' % SITE_URL)
    text = text.replace('src="/', 'src="%s/' % SITE_URL)

    notyet = "notyet" in tags
    if notyet:
      tags.remove("notyet")

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

    no_tags_no_ws = re.sub('<[^>]*>', '', re.sub('\s',' ',text)).strip()
    meta = ('<meta name="description" content="%s..." />' % no_tags_no_ws[:400] + " " +
            '<meta name="keywords" content="%s" />' % ', '.join(tags))

    text = "<p>" + text

    tag_block = ""
    if tags:
      tag_block = ", ".join(
        '<i><a href="%s/%s.html">%s</a></i>' % (URL_DIR, tag, tag)
        for tag in tags)

    guid=link

    
    if fb_tag:
      comments_full_url = "%s/%s" % (COMMENTS_URL, fb_tag)
      fb_link = '<a href="https://www.facebook.com/jefftk/posts/%s">facebook</a>' % (
        fb_tag.replace("status/", ""))

      comments_links = fb_link

      if gp_tag:
        gp_link = '<a href="https://plus.google.com/%s/posts/%s">google plus</a>' % (
          GP_UID, gp_tag)
        comments_links = "%s, %s," % (gp_link, comments_links)

        comments_full_url += "/" + gp_tag

      rss_comments_note = "<p><i>Comment on %s or write jeff@jefftk.com</i>" % comments_links
    else:
      rss_comments_note = ""
      comments_full_url = ""


    rss_include_item = n < RSS_MAX and not notyet
    if rss_include_item:
      w('    <item>')
      w('      <guid>%s</guid>' % guid)
      w("      <title>%s</title>" % title)
      w("      <link>%s</link>" % link)

    month, day, year = date.split()[1:4]

    if rss_include_item:
      t = text + rss_comments_note
      w("      <pubDate>%s %s %s 08:00:00 EST</pubDate>" % (day, month[:3], year))
      w("      <description>%s</description>" %
        t.replace("&", "&amp;").replace("<","&lt;").replace(">", "&gt;"))
      w("    </item>")

    title_and_body = ('<div class="content"><i class="date">%s</i><h3><a href="%s">%s</a>'
                      '</h3>\n%s</div>\n' % (date, link, title, text))

    per_file = open(os.path.join(OUT_DIR, link_anchor + ".html"), "w")

    per_file.write("<html>\n")
    per_file.write("  <head><title>%s</title>%s%s%s</head>\n" % (title, meta, css, GA_STR))
    per_file.write("  <body>%s<hr>%s<p>" % (links_partial(tag_block), title_and_body))

    if comments_full_url:
      per_file.write('<div style="max-width: 33em;">')
      per_file.write('<script src="%s"></script>' % comments_full_url)
      per_file.write('</div>')

    write_links_footer(per_file, tag_block)
    per_file.close()

    if not notyet:
      front_page_list.append('   <tr><td><small>%s</small>'
                             '       <td><small>%s</small>'
                             '       <td><small>%s</small>'
                             '       <td><a href="%s">%s</a></tr>\n' % (
        year, month[:3], tidy_day(day), link, title))

    tags.add("all")
    for tag in tags:
      if tag not in tag_to_items:
        tag_to_items[tag] = []
      if not notyet:
        tag_to_items[tag].append((year, month, day, link, title))


  for tag, item_list in tag_to_items.items():
    t = open(os.path.join(OUT_DIR, "%s.html" % tag), "w").write
    t("<html>\n")
    t("  <head><title>Jeff :: Posts :: %s</title>%s</head>\n" % (tag, GA_STR))
    t('  <body>%s<hr><h2>Posts :: %s</h2>\n<table border="0">\n' % (links_partial(), tag))
    for year, month, day, link, title in item_list:
      t('   <tr><td>%s<td>%s<td>%s<td><a href="%s">%s</a></tr>\n' % (
        year, month, day, link, title))
    t('  </table>\n')
    t('  <hr>%s\n' % links_partial())
    t('  </body>\n')
    t('</html>\n')

  write_footer()

  edit_front_page(front_page_list)

def tidy_day(day):
  d = str(int(day))
  suffix = "th"
  if d[-1] == '1':
    suffix = "st"
  elif d[-1] == '2':
    suffix = "nd"
  elif d[-1] == '3':
    suffix = "rd"
  return d + suffix

if __name__ == "__main__":
  start()
