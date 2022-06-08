#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
usage:

  python makerss.py && python reverserss.py

I find this elisp useful:

  (defun start-news-entry ()
    (interactive)
    (insert (format-time-string
       "  <a name=\"%Y-%m-%d\"></a><h3>%A %B %d %Y:</h3>"))
    (newline)
    (insert "  <div class=\"pt\">")  (newline)  (newline)
    (insert "    <h3></h3>") (newline)
    (insert "    <h4>Tags: notyet</h4>") (newline) (newline) (newline)
    (insert "  </div>") (newline))

  (require 'subr-x)
  (defun process-sentinel (process event_type)
    (message (format "%s: %s%s" process
                     (string-trim event_type)
                     (if (string= event_type "finished\n")
                         ""
                         " (see buffer make-rss)"))))

  (defun publish-news-entries ()
    (interactive)
    (message "publishing news entries in the background...")
    (start-process "make-rss" "make-rss" "~/bin/makerss-and-reverserss.sh")
    (set-process-sentinel (get-process "make-rss") 'process-sentinel))

"""

import sys, os, re, random, shutil, stat, subprocess
from lxml import etree
import lxml.html
from copy import deepcopy
from collections import defaultdict
import json

USE_DOUBLECLICK=True

def relative_to_absolute(pathname):
  return os.path.join(os.path.dirname(__file__), pathname)

def load_snippet(snippet_name):
  return open(relative_to_absolute(
    os.path.join("snippets", snippet_name))).read().strip()

def load_html_js_snippet(snippet_name):
  return '<script nonce="{{NONCE}}" type="text/javascript">%s</script>' % load_snippet(snippet_name)

class Configuration:
  def __init__(self):
    self.site_url = 'https://www.jefftk.com'
    self.site_dir = '/home/jefftk/jtk'
    self.in_html = 'news_raw.html'
    self.front_page = "index.html"
    self.out = 'news'
    self.posts = 'p'
    self.rss = 'news.rss'
    self.rss_full = 'news_full.rss'
    self.openring_filename = "current-openring.html"

    self.rss_description = "Jeff Kaufman's Writing"

    # How many posts to put in the rss feed.
    self.rss_max = 30

    # How many posts to put on the front page.
    self.front_page_max = 6

    # Author's UID on Google Plus
    self.google_plus_uid = "103013777355236494008"

    self.break_token = '~~break~~'

    self.notyet_token = 'notyet'
    self.nolw_token = 'nolw'

    self.max_update_chars = 500

  def full_url(self, leaf):
    return os.path.join(self.site_url, leaf)

  def full_filename(self, leaf):
    if leaf.startswith('/'):
      leaf = leaf[1:]
    return os.path.join(self.site_dir, leaf)

  def post_url(self, post):
    return os.path.join(self.posts, post.name)

  def relative_url(self, leaf):
    return '/%s' % leaf

  def front_page_fname(self):
    return self.full_filename(self.front_page)

  def new(self, fname):
    return '%s-new' % fname

  def prev(self, fname):
    return '%s-prev' % fname

config = Configuration()

INTROS = json.load(open(relative_to_absolute("intros.json")))

BEST_POSTS = json.load(open(relative_to_absolute("best_posts.json")))

SNIPPETS = {
  'rss_header': '''\
<?xml version="1.0" encoding="ISO-8859-1" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">

  <channel>
    <atom:link href="%s" rel="self" type="application/rss+xml" />
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <language>en-us</language>''' % (
      config.full_url(config.rss),
      config.rss_description,
      config.full_url(config.posts),
      config.rss_description),

  'rss_footer': '\n</channel>\n</rss>',
}

def edit_front_page(front_page_list):
  front_page = config.front_page_fname()
  front_page_tmp = config.new(config.front_page_fname())
  with open(front_page) as inf:
    with open(front_page_tmp, 'w') as outf:
      skipping = False
      for line in inf:
        if '<!-- end recent thoughts -->' in line:
          for entry in front_page_list:
            outf.write(entry)
            outf.write('\n')
          skipping = False

        if not skipping:
          outf.write(line)

        if '<!-- begin recent thoughts -->' in line:
          skipping = True

      assert not skipping

  os.rename(front_page_tmp, front_page)

def quote(s):
  return s.replace('&', '&amp;').replace('<','&lt;').replace('>', '&gt;').replace('"', '&quot;')

def title_to_url_component(s):
  s = s.lower()
  s = s.replace("'", "").replace('"', "")
  s = re.sub("[^A-Za-z0-9]", "-", s)
  s = re.sub("-+", "-", s)
  s = re.sub("^-*", "", s)
  s = re.sub("-*$", "", s)
  return s

def dimensions(link_ondisk):
  link_ondisk_dims = '%s.dimensions' % link_ondisk
  dims = None
  if os.path.exists(link_ondisk_dims):
    with open(link_ondisk_dims) as inf:
      dims = inf.read().strip()
  if not dims:
    identify_output = subprocess.check_output(['identify', link_ondisk])
    dims = identify_output.split()[2].decode('utf-8')
    with open(link_ondisk_dims, 'w') as outf:
      outf.write(dims)
  width, height = dims.split('x')
  return int(width), int(height)

class Update:
  def __init__(self, slug, post, element):
    self.anchor = 'update-%s' % slug
    self.slug = slug
    self.year, self.numeric_month, self.day = slug.split('-')
    self.short_month = {'01': 'Jan',
                        '02': 'Feb',
                        '03': 'Mar',
                        '04': 'Apr',
                        '05': 'May',
                        '06': 'Jun',
                        '07': 'Jul',
                        '08': 'Aug',
                        '09': 'Sep',
                        '10': 'Oct',
                        '11': 'Nov',
                        '12': 'Dec'}[self.numeric_month]
    self.post = post
    self.element = element
    self.title = 'Update %s' % slug

  def link(self):
    return self.post.link() + '#%s' % self.anchor

  def rss(self):
    html = etree.tostring(
      self.element, method='html', pretty_print=True).decode('utf-8')
    html = re.sub('.*(<b>Update %s</b>)', '', html)
    if len(html) > config.max_update_chars:
      html = html[:500] + '...'

    return '''
<item>
  <guid>%s</guid>
  <title>%s</title>
  <link>%s</link>
  <category>update_rss</category>
  <pubDate>%s %s %s 08:00:00 EST</pubDate>
  <description>%s</description>
</item>''' % (
  config.relative_url(self.link()),
  quote(self.title),
  config.full_url(self.link()),
  self.day, self.short_month, self.year,
  quote(html))

def hidden_topic(tag):
  return tag in ["all", "lwfeed"]

TAG_RENAMING = {
  "giving": "ea",
}

class Post:
  def __init__(self, slug, date, title, tags, element, openring):
    self.slug = slug
    self.date = date
    self.title = title
    self.published = config.notyet_token not in tags
    yeslw = config.nolw_token not in tags

    tags = [TAG_RENAMING.get(x, x) for x in tags
            if x != config.notyet_token and x != config.nolw_token]
    if yeslw:
      tags.append("lwfeed")
    self.name = title_to_url_component(title)
    self.element = element
    self.openring = openring
    self.updates = {}

    # these are filled in externally for published posts
    self.older_post = None
    self.newer_post = None
    # this is filled in externally for all posts
    self.posts_by_slug = None

    self.month, self.day, self.year = date.split()[1:4]
    self.short_month = self.month[:3]

    self.fb_link = None

    services = []
    for tag in tags:
      if '/' not in tag:
        continue
      service, token = tag.split('/', 1)
      if service == 'g+':
        services.append((1, 'google plus', 'gp',
                         'https://plus.google.com/%s/posts/%s' % (
                           config.google_plus_uid, token), token))
      elif service == 'fb':
        if token.startswith('note/'):
          token = token[len('note/'):]
          fb_link = 'https://www.facebook.com/note.php?note_id=%s' % token
        else:
          token = token.split('_')[-1]
          fb_link = 'https://www.facebook.com/jefftk/posts/%s' % token
          self.fb_link = fb_link
        services.append((2, 'facebook', 'fb', fb_link, token))
      elif service == 'lw':
        lw_link = 'https://lesswrong.com/%s' % token
        services.append((3, 'lesswrong', 'lw', lw_link, token))
      elif service == 'ea':
        suffix = 'posts'
        if token.startswith('old/'):
          _, token = token.split('/', 1)
          suffix = 'ea'
        ea_link = 'https://forum.effectivealtruism.org/%s/%s' % (suffix, token)
        services.append((4, 'the EA Forum', 'ea', ea_link, token))
      elif service == 'r':
        subreddit, post_id = token.split('/')
        r_link = 'https://www.reddit.com/r/%s/comments/%s' % (
          subreddit, post_id)
        services.append((5, 'r/%s' % subreddit, 'r', r_link, token))
      elif service == 'hn':
        services.append((6, 'hacker news', 'hn',
                         'https://news.ycombinator.com/item?id=%s' % token,
                         token))

    # sort by and then strip off priorities
    self.services = [x[1:] for x in sorted(services)]
    self.tags = list(sorted(set(x for x in tags if '/' not in x)))

    for possible_update in element.findall('.//b'):
      update_text = possible_update.text
      if update_text and update_text.startswith('Update '):
        match = re.match(r'Update (\d\d\d\d-\d\d-\d\d)', update_text)
        if match:
          update_slug, = match.groups()
          update = Update(update_slug, self, possible_update.getparent())
          if update.anchor in self.updates:
            raise Exception('Duplicate anchor %s on %s' % (
              update.anchor, title))
          self.updates[update.anchor] = update

          # make it possible to link to this update
          parent = possible_update.getparent()
          parent.insert(parent.index(possible_update),
                        etree.Element('a', name=update.anchor))

    for img in element.findall('.//img'):
      src = img.get('src')
      if src and src.startswith('/'):
        src_ondisk = config.full_filename(src[1:])
        width, height = dimensions(src_ondisk)
        if bool(img.get('width')) != bool(img.get('height')):
          raise Exception('bad image %s in %s' % (
            etree.tostring(img, method='html'), title))
        if not img.get('width'):
          img.set('width', str(width))
          img.set('height', str(height))
          max_width = 100.0
          img.set('class', 'mobile-fullwidth')
          img.set('style', 'max-width:%.1fvw; max-height:%.1fvw;' %
                  (max_width, max_width * height / width))

        if not img.get('srcset'):
          fname, ext = src.rsplit('.', 1)
          if ext in ['jpg', 'png']:
            srcsets = []
            for sizing in ['2x', '3x', '4x']:
              newsrc = '%s-%s.%s' % (fname, sizing, ext)
              for suffix in ['-sm', '-small', '-tn', '-1x']:
                if fname.endswith(suffix):
                  newsrc = '%s-%s.%s' % (fname[:-len(suffix)], sizing, ext)
              newsrc_ondisk = config.full_filename(newsrc)
              if os.path.exists(newsrc_ondisk):
                newwidth, _ = dimensions(newsrc_ondisk)
                srcsets.append('%s %sw' % (newsrc, newwidth))
            if srcsets:
              srcsets.insert(0, '%s %sw' % (src, width))
              img.set('srcset', ','.join(srcsets))

  def link(self):
    return os.path.join(config.posts, self.name)

  def bare_html(self, element):
    # don't include the wrapping div
    return '<p>' + '\n'.join(self.stringify_(x) for x in element.findall('*'))

  def blog_entry_summary(self):
    element = deepcopy(self.element)
    removing = False
    for child in element.findall('.//*'):
      if child.text and config.break_token in child.text:
        child.text, _ = child.text.split(config.break_token)
        removing = True
        child.tail = ''
      elif child.tail and config.break_token in child.tail:
        child.tail, _ = child.tail.split(config.break_token)
        removing = True
      elif removing:
        child.getparent().remove(child)

    link = config.relative_url(self.link())
    append_more = "%s<a href='%s'>%s...</a>" % (
      ' ' if removing else '<p>', link, 'more' if removing else 'full post')
    html = self.stringify_(element) + append_more

    return '''\
<div class=blog-entry-summary>
  <div class=blog-entry-date><a
     class=invisible-link href='%s'>%s %s, %s</a></div>
  <div class=blog-entry-title><a class=invisible-link href='%s'>%s</a></div>
  <div class=blog-entry-beginning>
    <p>%s
  </div>
</div>''' % (link, self.month, tidy_day(self.day), self.year,
             link, self.title, html)

  def html(self, is_amp):
    element = deepcopy(self.element)

    for tt in element.findall('.//tt'):
      tt.tag = 'code'

    if not self.published:
      element.insert(0, parse('<p><i>draft post</i></p>'))

    amp_styles = set()
    amp_external = set()

    if is_amp:
      for styled in element.findall('.//*[@style]'):
        style = styled.attrib.pop('style')
        auto_id = 'inline-style-%s' % abs(hash(style))
        amp_styles.add('#%s {%s}' % (auto_id, style))
        assert not styled.get('id')
        styled.set('id', auto_id)

      for style_block in element.findall('.//style'):
        amp_styles.add(style_block.text)
        style_block.getparent().remove(style_block)

      for img in element.findall('.//img'):
        img.tag = 'amp-img'
        img.set('layout', 'responsive')

        try:
          border = img.attrib.pop('border')
        except KeyError:
          pass

      for iframe in element.findall('.//iframe'):
        if 'youtube' in iframe.get('src'):
          amp_external.add('youtube')
          iframe.tag = 'amp-youtube'
          videoid, = re.findall('/embed/([^?]*)', iframe.get('src'))
          attrib = iframe.attrib
          width, height = attrib['width'], attrib['height']
          attrib.clear()
          attrib['width'], attrib['height'] = width, height
          attrib['layout'] = 'responsive'
          attrib['data-videoid'] = videoid
        else:
          amp_external.add('iframe')
          iframe.tag = 'amp-iframe'

          try:
            placeholder_img = iframe.attrib.pop('data-placeholder')
            iframe.append(etree.Element(
              'amp-img', placeholder='', layout='fill', src=placeholder_img))
          except KeyError:
            pass

          iframe.set('sandbox', 'allow-scripts allow-same-origin')
    else:
      # make youtube responsive
      for iframe in element.findall('.//iframe'):
        if 'youtube' in iframe.get('src'):
          width, height = iframe.attrib['width'], iframe.attrib['height']
          del iframe.attrib['width']
          del iframe.attrib['height']
          div = etree.Element('div')
          div.attrib['style'] = (
            'position: relative;'
            'padding-bottom: %.2f%%;'
            'height: 0;'
            'overflow: hidden;'
            'max-width: 100%%;') % (100 * float(height) / float(width))
          iframe.attrib['style'] = (
            'position: absolute;'
            'top: 0;'
            'left: 0;'
            'width: 100%;'
            'height: 100%;')
          parent = iframe.getparent()
          iframe_index = list(parent).index(iframe)
          parent.remove(iframe);
          parent.insert(iframe_index, div)
          div.append(iframe)

    no_tags_no_ws = re.sub('<[^>]*>', '',
                           re.sub('\s+',' ',
                                  re.sub('<style>[^<]*</style>', '',
                                         self.bare_html(element)))).strip()

    head = etree.Element('head')
    head.append(etree.Element(
      'meta', name='description', content=no_tags_no_ws[:400]))
    head.append(etree.Element(
      'meta', name='keywords', content=', '.join(self.tags)))
    head.append(etree.Element(
      'meta', name='viewport', content=load_snippet('meta_viewport.html')))
    head.append(etree.Element('meta', charset='utf-8'))

    if is_amp:
      head.append(etree.Element(
        'script', **{'async':'', 'src':'https://cdn.ampproject.org/v0.js'}))

    if is_amp:
      head.append(etree.Element('link', rel='canonical',
                                href=config.relative_url(self.link())))
    else:
      head.append(etree.Element('link', rel='amphtml', href='%s.amp' % (
        config.relative_url(self.link()))))

    if is_amp:
      head.append(parse('''\
<script nonce="{{NONCE}}" async custom-element="amp-ad"
   src="https://cdn.ampproject.org/v0/amp-ad-0.1.js"></script>'''))
    else:
      head.append(parse('''\
<script nonce="{{NONCE}}" async='async' src='https://www.googletagservices.com/tag/js/gpt.js'></script>'''))
      head.append(parse('''\
<script nonce="{{NONCE}}">
  var googletag = googletag || {};
  googletag.cmd = googletag.cmd || [];
</script>'''))
      head.append(parse('''\
<script nonce="{{NONCE}}">
  googletag.cmd.push(function() {
      googletag.pubads().setForceSafeFrame(true).setSafeFrameConfig({useUniqueDomain: true});
      var maxAdWidth = 550;
      if (window.innerWidth >= 1030 || window.innerWidth < 850) {
        maxAdWidth =  window.innerWidth - 16;
      }
      googletag.defineSlot('/21707489405/post_bottom_square', {
         'fixed': [300, 250],
         'max': [maxAdWidth, 400],
      }, 'div-gpt-ad-1524882696974-0').addService(googletag.pubads());
  googletag.pubads().enableSingleRequest();
  googletag.enableServices();
});
</script>'''))

    title = etree.Element('title')
    title.text = self.title
    head.append(title)

    body = etree.Element('body')

    if is_amp:
      amp_external.add('analytics')
      body.append(parse(load_snippet('google_analytics_amp.html')))
    else:
      head.append(parse(load_html_js_snippet('google_analytics_nonamp.js')))

    if not is_amp:
      head.append(parse(load_html_js_snippet('hover_preview.js')))

    # TODO: look into ld json schema for amp

    if is_amp:
      head.append(parse(load_snippet('amp_boilerplate.html')))
      head.append(parse(load_snippet('amp_noscript_boilerplate.html')))

    head.append(parse(
      '<style%s>%s%s</style>' % (
        ' amp-custom=""' if is_amp else '',
        load_snippet('post.css'),
        '\n'.join(sorted(amp_styles)))))

    wrapper = etree.Element('div', id='wrapper')

    wrapper.append(parse(links_partial()))
    wrapper.append(etree.Element('hr'))

    content = etree.Element('div')
    content.set('class', 'content')

    fancy_date = '%s %s, %s' % (self.month, tidy_day(self.day), self.year)

    tag_block = ''
    if self.tags:
      tag_block = '<span>%s</span>&nbsp;&nbsp;<small><tt>%s</tt></small>' % (
        ', '.join(
          '<i><a href="/news/%s">%s</a></i>' % (tag, tag)
          for tag in self.tags
          if tag != "lwfeed"),
        '[amp]' if is_amp else '[html]')

    content.append(parse('''<table id="title-date-tags">
    <tr><td valign="top" rowspan="2"><h3><a href="%s">%s</a></h3></td>
        <td align="right" valign="top">%s</td></tr>
    <tr><td align="right" valign="top">%s</td></tr></table>''' % (
      config.relative_url(self.link()), self.title, fancy_date, tag_block)))

    content.append(element)

    if self.newer_post:
      newer_section='''\
<a id=newer href="%s">
  <div class=arr>
    &larr;
  </div>
  %s
</a>''' % (config.relative_url(self.newer_post.link()),
           self.newer_post.title)
    else:
      newer_section='<div id=newer-blank></div>'

    older_section = ''
    if self.older_post:
      older_section = '''\
<a id=older href="%s">
  %s
  <div class=arr>
    &rarr;
  </div>
</a>''' % (config.relative_url(self.older_post.link()),
           self.older_post.title)

    content.append(parse('<div id=newer-older>%s%s</div>' % (
      newer_section, older_section)))

    if self.services:
      content.append(parse('<p>Comment via: %s</p>\n' % (
        ', '.join('<a href="%s">%s</a>' % (service_link, service_name)
                  for service_name, _, service_link, _ in self.services))))
      if is_amp:
        comment_thread = etree.Element('div')
        comment_thread.set('class', 'comment-thread')
        comments = etree.Element('div', id='comments')
        comments.append(comment_thread)
        content.append(comments)

        amp_external.add('list')
        amp_external.add('mustache')

        comment_thread.append(parse('''
<amp-list width=auto height=500 layout="fixed-height" src=%s>
  <template type="amp-mustache">
    <div class=comment id="{{anchor}}">
      <a dontescapethis="{{source_link}}">{{{author}}}</a> ({{service}})
      <a dontescapethis="#{{anchor}}" class=commentlink></a>
      <p>{{{text}}}
    </div>
  </template>
  <div overflow>See more</div>
</amp-list>
''' % ('/wsgi/amp-json-comments?%s' % (
  '&'.join('%s=%s' % (service_abbr, service_token)
           for _, service_abbr, _, service_token in self.services)))))

      else:
        content.append(parse('''\
<div id="comments">
%s
<script nonce="{{NONCE}}" type="text/javascript">
%s
</script>
</div>''' % (
  load_html_js_snippet('comment_script.js'),
  '\n'.join(
    "pullComments('/wsgi/json-comments/%s/%s', '%s');\n" % (
      service_abbr, service_tag, service_name)
    for service_name, service_abbr, service_link, service_tag
    in self.services))))

    wrapper.append(content)

    wrapper.append(self.openring)

    wrapper.append(parse('<p>'))
    if is_amp:
      if USE_DOUBLECLICK:
        wrapper.append(parse('''\
<p>
<amp-ad width=300 height=250
  type="doubleclick"
  data-slot="/21707489405/post_bottom_square">
</amp-ad>'''))
      else:
        wrapper.append(parse('''\
<p>
<amp-ad width="100vw" height="320" type="adsense"
  data-ad-client="ca-pub-0341874384016383"
  data-ad-slot="4122621225"
  data-auto-format="rspv"
  data-full-width>
    <div overflow></div>
</amp-ad>'''))

    else:
      wrapper.append(parse('''\
<div id="ad-wrapper">
<div id='div-gpt-ad-1524882696974-0'>
  <script nonce="{{NONCE}}">
    googletag.cmd.push(function() { googletag.display('div-gpt-ad-1524882696974-0'); });
  </script>
</div>
</div>
'''))

    best_post_slugs = []
    while len(best_post_slugs) < 5:
      slug, = random.choices(
        population=([slug for (slug, _, _) in BEST_POSTS]),
        weights=([weight for (_, _, weight) in BEST_POSTS]),
        k=1)
      if slug not in best_post_slugs:
        best_post_slugs.append(slug)

    best_posts = [self.posts_by_slug[slug] for slug in best_post_slugs]

    best_posts_html = '<p><b>More Posts</b></p><ul>%s</ul>' % (
      ''.join('<li><p><a href="%s">%s</a></p></li>' % (
        config.relative_url(other.link()),
        other.title) for other in best_posts))

    preview_iframe_html = (
      '<div id=preview><iframe id=preview-iframe scrolling=no '
      'sandbox="allow-same-origin"></iframe>'
      '<button id=preview-open>open</button></div>')

    wrapper.append(parse(
      '<div id="right-column"><div id="top-posts">%s</div>%s</div>' % (
        best_posts_html,
        '' if is_amp else preview_iframe_html)))


    wrapper.append(etree.Element('hr'))
    wrapper.append(parse(links_partial()))

    body.append(wrapper)

    page = etree.Element('html', lang='en')
    if is_amp:
      page.set('amp', 'amp')
    page.append(head)
    page.append(body)

    if is_amp:
      for external in amp_external:
        external_type = 'element'
        version = '0.1'
        if external == 'mustache':
          external_type = 'template'
          version = '0.2'
        ce_script = etree.Element(
          'script', **{
            'async':'',
            'src':'https://cdn.ampproject.org/v0/amp-%s-%s.js' % (external, version)})
        ce_script.set('custom-%s' % external_type, 'amp-%s' % external)
        ce_script.tail = '\n'
        head.append(ce_script)

    return '<!doctype html>\n%s' % etree.tostring(
      page, method='html', pretty_print=True).decode('utf-8').replace(
        config.break_token, '').replace('dontescapethis', 'href')

  def stringify_(self, element):
    return etree.tostring(
      element, method='html', pretty_print=True).decode(
        'utf-8').replace(config.break_token, '')

  def rss(self):
    element = deepcopy(self.element)
    if self.services:
      comments_links = ', '.join(
        '<a href="%s">%s</a>' % (
          service_link, service_name)
        for (service_name, _, service_link, _) in self.services)
      element.append(parse('<p><i>Comment via: %s</i>' %
                                      comments_links))

    html = self.bare_html(element)
    # Temporary work-around for LW not handling relative URLs in RSS import
    # https://github.com/LessWrong2/Lesswrong2/issues/2434
    for prefix in ['href="', 'src="', 'srcset="', ' 550w,']:
      html = html.replace("%s/" % prefix, '%s%s/' % (prefix, config.site_url))

    return '''
<item>
  <guid>%s</guid>
  <title>%s</title>
  <link>%s</link>
  %s
  <pubDate>%s %s %s 08:00:00 EST</pubDate>
  <description>%s</description>
</item>''' % (
  config.relative_url(self.link()),
  quote(self.title),
  config.full_url(self.link()),
  '\n  '.join('<category>%s</category>' % tag
            for tag in sorted(self.tags)),
  self.day, self.short_month, self.year,
  quote(html))

def parse(s):
  try:
    return lxml.html.fragment_fromstring(s, create_parent=False)
  except:
    print(s)
    raise

def parsePosts():
  posts = []
  published_posts = []
  posts_by_name = {}
  posts_by_slug = {}

  raw_fname = config.full_filename(config.in_html)
  cleaned_fname = raw_fname + '.tmp'
  with open(raw_fname) as inf:
    with open(cleaned_fname, 'w') as outf:
      raw_text = inf.read()
      for f, r in [('“', '"'),
                   ('”', '"'),
                   ("’", "'")]:
        raw_text = raw_text.replace(f, r)
      outf.write(raw_text)

  with open(config.full_filename(config.openring_filename)) as inf:
    openring = parse(inf.read())

  with open(cleaned_fname) as inf:
    tree = etree.parse(inf, etree.HTMLParser())
    body = tree.find('body')

    prev = None
    prev_prev = None

    for element in body.findall('*'):
      # Posts are divs
      # Post metadata is right before each div, in first an a and then an h3
      # Yes, this is silly, not changing it now.

      if element.tag == 'div':
        assert prev.tag == 'h3'
        assert prev_prev.tag == 'a', element.findall('*')[0].text

        slug = prev_prev.get('name')
        date = prev.text[:-1]

        post_elements = element.findall('*')
        title_h3 = post_elements[0]
        try:
          tags_h4 = post_elements[1]
        except Exception:
          print(post_elements)
          print(title_h3.text)
          raise
        assert title_h3.tag == 'h3'
        title = title_h3.text
        assert tags_h4.tag == 'h4'
        tags_raw = tags_h4.text
        assert tags_raw.startswith('Tags:')
        tags = [x.strip() for x in tags_raw[len('Tags:'):].split(',')]

        # Remove the title and tags now that we're done with them.
        element.remove(title_h3)
        element.remove(tags_h4)

        if tags_h4.tail:
          # don't lose this text
          first = etree.Element('span')
          first.text = tags_h4.tail
          element.insert(0, first)

        if not title:
          print(post_elements)

        post = Post(slug, date, title, tags, element, openring)

        posts.append(post)
        if post.published:
          published_posts.append(post)

        if post.name in posts_by_name:
          raise Exception('Duplicate post title: %r and %r' % (
            posts_by_name[post.name].title, post.title))
        posts_by_name[post.name] = post

        if post.slug in posts_by_slug:
          raise Exception('Duplicate post slug: %r for %r and %r' % (
            post.slug, posts_by_slug[post.slug].title, post.title))
        posts_by_slug[post.slug] = post
        post.posts_by_slug = posts_by_slug

      prev_prev = prev
      prev = element

  # Now that we've loaded all the posts, update links to use pretty
  # names and not slugs.
  #for post in posts:
  #  for anchor in post.element.findall('.//a'):
  #    href = anchor.get('href')
  #    if href:
  #      match = re.match(r'(\d\d\d\d-\d\d-\d\d)', href)
  #      if match:
  #        slug, = match.groups()
  #        new_href = config.relative_url(posts_by_slug[slug].link())
  #        anchor.set('href', new_href)

  for published_post_earlier, published_post_later in zip(
      published_posts[1:], published_posts):
    published_post_earlier.newer_post = published_post_later
    published_post_later.older_post = published_post_earlier

  return posts

def links_partial():
  return '''
<div class="headfoot">
  <li><a href="/" rel="author">Jeff Kaufman</a></li>
  <li><a href="/p/index">Posts</a></li>
  <li><a href="/news.rss">RSS</a></li>
  <li><a href="__REVERSE_RSS__">&#9666;&#9666;RSS</a></li>
  <li><a href="/contact">Contact</a></li>
</div>
'''

def delete_old_staging():
  for modifier in [config.new, config.prev]:
    for directory in [config.out, config.posts]:
      full_directory = config.full_filename(modifier(directory))
      try:
        shutil.rmtree(full_directory)
      except FileNotFoundError:
        pass

    for fname in [config.rss, config.rss_full]:
      try:
        full_fname = config.full_filename(modifier(fname))
      except FileNotFoundError:
        pass

def make_new_staging():
  for directory in [config.out, config.posts]:
    os.mkdir(config.full_filename(config.new(directory)))

def start():
  delete_old_staging()
  make_new_staging()

  front_page_list = []
  tag_to_posts = defaultdict(list)

  rss_entries = {} # (slug | update_slug-original_slug) -> entry


  fb_links = []

  for post in parsePosts():
    fname_base = config.full_filename(
      os.path.join(config.new(config.posts), post.name))
    fname_slug = config.full_filename(
      os.path.join(config.new(config.out), post.slug)) + '.html'
    with open(fname_base + '.html', 'w') as outf:
      outf.write(post.html(is_amp=False))
    with open(fname_base + '.amp.html', 'w') as outf:
      outf.write(post.html(is_amp=True))
    shutil.copy(fname_base + '.html', fname_slug)
    st = os.stat(fname_slug)
    os.chmod(fname_slug, st.st_mode & (stat.S_IRUSR | stat.S_IWUSR))

    if post.published:
      if len(front_page_list) < config.front_page_max:
        front_page_list.append(post.blog_entry_summary())

      tags = set(['all']).union(post.tags)
      for tag in tags:
        tag_to_posts[tag].append(post)

      rss_entries[post.slug] = post.rss()
      for update in post.updates.values():
        rss_entries['%s-%s' % (update.slug, post.slug)] = update.rss()

      if post.fb_link:
        fb_links.append([post.title, post.date, post.fb_link])

  with open(config.full_filename("fblinks.html"), 'w') as outf:
    outf.write("<ul>\n")
    for title, date, fb_link in fb_links:
      outf.write('<li>%s <a href="%s">%s</a>\n' % (
        date, fb_link, title))
    outf.write("</ul>\n")

  rss_entries = list(reversed([
    entry for _, entry in sorted(rss_entries.items())]))
  for rss_file in [config.rss, config.rss_full]:
    with open(config.full_filename(
        config.new(rss_file)), 'w') as outf:
      outf.write(SNIPPETS['rss_header'])
      for n, rss_entry in enumerate(rss_entries):
        if rss_file == config.rss_full or n < config.rss_max:
          outf.write(rss_entry)
      outf.write(SNIPPETS['rss_footer'])

  tag_json = {}

  for tag, tag_posts in tag_to_posts.items():
    if tag == 'all':
      rss_link = '/news.rss'
    else:
      rss_link = '/news/%s.rss' % tag

    tag_json[tag] = [post.link() for post in tag_posts]

    entries = '\n'.join('''\
<li><a href="%s">
  <div class=title>%s</div>
  <div class=date>%s %s, %s</div></a></li>''' % (
    config.relative_url(post.link()), post.title, post.month,
    post.day, post.year) for post in tag_posts)

    with open(config.full_filename(os.path.join(
        config.new(config.out), '%s.html' % tag)), 'w') as outf:
      outf.write('''\
<html>
<head>
  <title>%s</title>
  <meta name=viewport content="%s">
  <link rel=alternate type="application/rss+xml" title="RSS Feed" href="%s">
  %s
</head>
<body>
<style>
h2 { margin: .5em }
body {
   margin: 0;
   padding: 0;
}
#content {
  max-width: 550px;
  margin-left: auto;
  margin-right: auto;
}
#content li { list-style-type: none; margin: 0 }
#content li a { display: block; padding: .75em }
#content li a:link { text-decoration: none }
.title:hover { text-decoration: underline }
#content ul { margin: 0; padding: 0 }
#content li:nth-child(odd) {
  background: #EEE;
}
.date { font-size: 85%% ; color: black }
.headfoot { margin: 3px }
.headfoot ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
.headfoot li {
  display: inline;
  margin-left: 5px;
  margin-right: 5px;
}
</style>
%s<hr>
<div id=content>
<h2>Posts :: %s (<a href="%s">rss</a>)</h2>
%s
<ul>
%s
</ul>
</div>
<hr>%s
</body>
</html>''' % (
  'Blog Posts' if tag == 'all' else 'Posts tagged %s' % tag,
  load_snippet('meta_viewport.html'),
  rss_link,
  load_html_js_snippet('google_analytics.js'),
  links_partial(),
  tag,
  rss_link,
  wrap_intro(INTROS.get(tag, "")),
  entries,
  links_partial()))

  edit_front_page(front_page_list)

  for x in [
      config.posts, config.out, config.rss, config.rss_full]:
    x = config.full_filename(x)

    os.rename(x, config.prev(x))
    os.rename(config.new(x), x)

  os.symlink(config.full_filename(os.path.join(config.out, 'all.html')),
             config.full_filename(os.path.join(config.out, 'index.html')))
  os.symlink(config.full_filename(os.path.join(config.out, 'all.html')),
             config.full_filename(os.path.join(config.posts, 'index.html')))

  with open(config.full_filename(
      os.path.join(config.out, 'tags.json')), "w") as outf:
    outf.write(json.dumps(tag_json))


  count_topics = [(len(posts), tag, wrap_intro(INTROS.get(tag, "")))
                  for (tag, posts) in tag_json.items()
                  if not hidden_topic(tag)]
  count_topics.sort(reverse=True)
  topics_lis = ['<li><p><a href="/news/%s">%s</a> (%s)%s</li>' % (
    topic, topic, count, intro) for (count, topic, intro) in count_topics]

  with open(config.full_filename(
      os.path.join(config.out, 'topics.html')), 'w') as outf:
    outf.write('''
<html>
<head>
  <title>Jeff :: Topics</title>
  <meta name=viewport content="%s">
</head>
<body>
<style>
h2 { margin: .5em }
body {
   margin: 0;
   padding: 0.5em;
   max-width: 40em;
}
#content {
  max-width: 550px;
  margin-left: auto;
  margin-right: auto;
}
</style>
</head>
<body>
<h1>Topics</h1>
<ul>
%s
</ul>
</body>
</html>
    ''' % (
      load_snippet('meta_viewport.html'),
      '\n'.join(topics_lis),
    ))

def wrap_intro(intro):
  if not intro:
    return ""

  return "<p>%s<p>" % (intro)

def tidy_day(day):
  d = str(int(day))
  suffix = 'th'
  if len(d) == 2 and d[0] == '1':
    suffix = 'th'
  elif d[-1] == '1':
    suffix = 'st'
  elif d[-1] == '2':
    suffix = 'nd'
  elif d[-1] == '3':
    suffix = 'rd'
  return d + suffix

if __name__ == '__main__':
  start()
