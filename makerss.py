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

    self.rss_description = "Jeff Kaufman's Writing"

    # How many posts to put in the rss feed.
    self.rss_max = 30

    # How many posts to put on the front page.
    self.front_page_max = 6

    # Author's UID on Google Plus
    self.google_plus_uid = "103013777355236494008"

    self.break_token = '~~break~~'

    self.notyet_token = 'notyet'

    self.max_update_chars = 500

  def full_url(self, leaf):
    return os.path.join(self.site_url, leaf)

  def full_filename(self, leaf):
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

BEST_POSTS = [
  ('2016-06-20', 'Mike Mulligan and His Obsolete Technology'),
  ('2016-06-15', 'Reading about guns'),
  ('2016-02-26', 'Make Buses Dangerous'),
  ('2016-01-16', 'Tiny House Movement'),
  ('2015-11-29', 'Giving vs Doing'),
  ('2015-11-20', 'Negative News'),
  ('2015-11-09', 'Thoughtful Non-consumption'),
  ('2015-10-20', 'How Bad Is Dairy?'),
  ('2015-10-07', 'Mercury Spill'),
  ('2015-08-11', 'Why Global Poverty?'),
  ('2015-07-24', 'Lyme Disease By County'),
  ('2015-06-27', 'Cheap College via Marrying'),
  ('2015-06-17', 'Subway Synchronization Protocol'),
  ('2015-05-14', 'Singular They FAQ'),
  ('2015-04-12', 'Instantiating Arguments'),
  ('2015-01-14', 'The Privilege of Earning To Give'),
  ('2014-12-25', "We Haven't Uploaded Worms"),
  ('2014-09-08', 'Policies'),
  ('2014-08-25', 'Persistent Idealism'),
  ('2014-07-14', 'The Economics of a Studio CD'),
  ('2014-07-01', 'Preparing for our CD'),
  ('2014-06-25', 'Optimizing Looks Weird'),
  ('2014-02-27', 'Playing to Lose'),
  ('2014-02-18', 'Dance Weekend and Festival Survey'),
  ('2014-01-26', 'Contra Dance Band Size'),
  ('2013-12-28', 'Getting Booked For Dances'),
  ('2013-10-22', 'OK to Have Kids?'),
  ('2013-10-01', 'John Wesley on Earning to Give'),
  ('2013-08-22', 'Rationing With Small Reserves'),
  ('2013-08-13', 'Simplest Interesting Game'),
  ('2013-07-21', 'Against Singular Ye'),
  ('2013-06-25', 'Is Pandora Really Exploiting Artists?'),
  ('2013-06-14', 'Is Unicode Safe?'),
  ('2013-06-06', 'Survey of Historical Stock Advice'),
  ('2013-05-28', 'Haiti and Disaster Relief'),
  ('2013-05-11', 'Keeping Choices Donation Neutral'),
  ('2013-04-01', 'The Unintuitive Power Laws of Giving'),
  ('2013-03-06', 'Getting Myself to Eat Vegetables'),
  ('2013-01-22', 'Debt Relief Is Bad Means Testing'),
  ('2012-10-30', 'Contra Cliquishness: Healthy?'),
  ('2012-10-03', 'Parenting and Happiness'),
  ('2012-09-21', 'Make Your Giving Public'),
  ('2012-09-17', 'Record Your Playing'),
  ('2012-09-11', 'Objecting to Situations'),
  ('2012-08-08', 'Artificial Recordings and Unrealistic Standards'),
  ('2012-08-07', 'Singular They: Towards Ungendered Language'),
  ('2012-07-14', 'Exercises'),
  ('2012-06-17', 'Altruistic Kidney Donation'),
  ('2012-03-29', 'Teach Yourself any Instrument'),
  ('2012-03-28', 'Brain Preservation'),
  ('2012-03-24', 'Insurance and Health Care'),
  ('2012-02-13', 'You Should Be Logging Shell History'),
  ('2012-02-03', 'Octaveless Bass Notes'),
  ('2011-12-29', 'Instrument Complexity and Automation'),
  ('2011-09-23', 'Letter From Our Crazy Ex-Landlord'),
  ('2011-12-03', 'A Right to Publicy'),
  ('2011-11-13', 'Personal Consumption Changes As Charity'),
  ('2011-11-02', 'Whole Brain Emulation and Nematodes'),
  ('2011-10-15', 'Local Action and Remote Donation'),
  ('2011-10-04', 'Online Community Aging'),
  ('2011-09-11', 'Mandolin Microphone Placement'),
  ('2011-09-09', 'Charities and Waste'),
  ('2011-08-08', 'Negative Income Tax'),
  ('2011-07-27', 'Belief Listing Project: Giving'),
  ('2011-07-18', 'Contra Dance Unplugged'),
  ('2011-07-15', 'Undisabling A Keyboard\'s Internal Speakers'),
  ('2011-06-18', 'Boston Apartment Prices Map'),
  ('2011-04-12', 'Giving Up On Privacy'),
  ('2011-01-08', 'Significant Whitespace In Expressions'),
  ('2010-12-05', 'Abstracting Compassion'),
  ('2010-11-17', 'Transit Service Quality Map'),
  ('2010-07-23', 'Tracking Down a Statistic: Does Fairtrade Work?'),
  ('2010-05-25', 'Putting Words Off-Limits'),
]

SNIPPETS = {
  'meta_viewport': 'width=device-width,minimum-scale=1,initial-scale=1',

  'google_analytics': r'''
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-27645543-1', 'auto');
  ga('send', 'pageview');
</script>
''',

  'google_analytics_nonamp': r'''
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-27645543-1', 'auto');
  ga('set', 'expId', 'zLjKaw9oRNayoqGxuudFVQ');
  ga('set', 'expVar', '0');
  ga('send', 'pageview',  {'dimension1': 'non-amp'});
</script>
''',

  'google_analytics_amp': '''
<amp-analytics type="googleanalytics">
<script type="application/json">
{
  "vars": {
    "account": "UA-27645543-1"
  },
  "extraUrlParams": {
    "cd1": "amp",
    "xid": "zLjKaw9oRNayoqGxuudFVQ",
    "xvar": "1"
  },
  "triggers": {
    "trackPageview": {
      "on": "visible",
      "request": "pageview"
    }
  }
}
</script>
</amp-analytics>''',

  'comment_script': r'''<script type="text/javascript">
var last_visit = document.cookie.replace(/(?:(?:^|.*;\s*)jtk_last_visit\s*\=\s*([^;]*).*$)|^.*$/, "$1");
var current_time = new Date().getTime();
var one_year_gmt_str = new Date(current_time + 31536000000).toGMTString();
document.cookie = "jtk_last_visit=" + current_time +
                          "; path=" + window.location.pathname +
                       "; expires=" + one_year_gmt_str;

function ajaxJsonRequest(url, callback) {
  function createRequestObject() {
    var tmpXmlHttpObject;
    if (window.XMLHttpRequest) {
        // Mozilla, Safari would use this method ...
        tmpXmlHttpObject = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        // IE would use this method ...
        tmpXmlHttpObject = new ActiveXObject("Microsoft.XMLHTTP");
    }
    return tmpXmlHttpObject;
  }
  var http = createRequestObject();

  //make a connection to the server ... specifying that you intend to make a GET request
  //to the server. Specifiy the page name and the URL parameters to send
  http.open('get', url);
  http.onreadystatechange = function() {
    if(http.readyState == 4){
      callback(JSON.parse(http.responseText));
    }
  }
  http.send(null);
}

all_comments = {};
quote_threshold = 8;
quoting= {}
dictionary = {}

function canonical_wordlist(s) {
  return (s.replace(/&[^ ;]+;/g, '')
           .replace(/<[^> ]+>/g, '')
           .toLowerCase()
           .replace(/[^a-z0-9 ]/g, '')
           .split(" "));
}

function build_phrase_dictionary_for_comment(comment, index) {
  var words = canonical_wordlist(comment);
  for (var i = 0 ; i + quote_threshold < words.length ; i++) {
    var phrase = [];
    for (var j = 0 ; j < quote_threshold ; j++) {
      phrase.push(words[i+j]);
    }
    phrase = phrase.join(" ");
    if (!dictionary[phrase]) {
      dictionary[phrase] = [];
    }
    dictionary[phrase].push(index);
  }
}

function build_phrase_dictionary(comments) {
  dictionary = {}
  for (var i = 0 ; i < comments.length; i++) {
    build_phrase_dictionary_for_comment(comments[i][3], i);
  }
  for (var phrase in dictionary) {
    if (dictionary[phrase].length < 2) {
      delete dictionary[phrase];
    }
  }
}

function find_quotes(comments) {
  build_phrase_dictionary(comments);

  // hash from quoter index to hash from quotee index to first quoted phrase
  var found_quotes = {};

  for (var phrase in dictionary) {
    var indexes = dictionary[phrase];
    var first = indexes[0];
    for (var i = 1 ; i < indexes.length ; i++) {
      var index = indexes[i];
      if (index != first) {
        if (!found_quotes[index]) {
          found_quotes[index] = {};
        }
        if (!found_quotes[index][first]) {
          found_quotes[index][first] = phrase;
        }
      }
    }
  }
  quoting = {};
  not_quoting = {}
  for (var i = 0 ; i < comments.length ; i++) {
    if (found_quotes[i]) {
      var quoted_comments_count = 0;
      var earlier_index = -1;

      // only give comments that quote exactly one earlier comment
      for (var x in found_quotes[i]) {
        quoted_comments_count += 1;
        earlier_index = x;
      }
      if (quoted_comments_count == 1) {
        quoting[i] = earlier_index;
      } else {
        if (!not_quoting[i]) {
          not_quoting[i] = [];
        }
        not_quoting[i].push([earlier_index, quoted_comments_count, found_quotes[i]]);
      }
    }
  }
}

function add_space_for_children(comments) {
  var new_comments = [];
  for (var i = 0 ; i < comments.length ; i++) {
    new_comments[i] = [];
    for (var j = 0 ; j < comments[i].length; j++) {
      new_comments[i].push(comments[i][j]);
    }
    if (new_comments[i].length == 5) {
      // server didn't leave a space for children; add one
      new_comments[i].push([]);
    }
  }
  return new_comments;
}

function nest(comments) {
  find_quotes(comments);
  // iterate backwards to make deletions safe
  for (var i = comments.length - 1 ; i >= 0 ; i--) {
    if (quoting[i]) {
      var earlier_index = quoting[i];
      comments[earlier_index][5].splice(0, 0, comments[i]);
      comments.splice(i,1);
    }
  }

  return comments;
}

function display_posts(comments) {
  return display_posts_helper(nest(comments));
}

function google_plus_color(i) {
  if (i % 6 == 0) {
    return '#004bf5';
  } else if (i % 6 == 1) {
    return '#e61b31';
  } else if (i % 6 == 2) {
    return '#feb90d';
  } else if (i % 6 == 3) {
    return '#004bf5';
  } else if (i % 6 == 4) {
    return '#e61b31';
  } else {
    return '#00930e';
  }
}

function service_abbr(service) {
  if (service == "google plus") {
    return 'g+';
  } else if (service == "lesswrong") {
    return 'lw';
  } else if (service == "hacker news") {
    return 'hn';
  } else if (service == "facebook") {
    return 'fb';
  } else {
    return service;
  }
}

function display_posts_helper(comments) {
  var h = ""
  for (var i = 0; i < comments.length; i++) {
    // h += "<hr>";
    // name, user_link, anchor, message, children
    var name = comments[i][0];
    var user_link = comments[i][1];
    var anchor = comments[i][2];
    var message = comments[i][3];
    var ts = comments[i][4];
    var children = comments[i][5];
    var service = comments[i][6];

    h += "<div class=comment id='" + anchor + "'>";
    h += "<div style='display:none'>ts=" + ts + "</div>";
    h += "<a href='" + user_link + "'>" + name + "</a> (";
    h += service_abbr(service) + "): ";
    h += "<a href='#" + anchor + "' class=commentlink>link</a>";
    h += "<div";
    if (last_visit.length > 0 && ts > last_visit/1000) {
      h += " class=newcomment";
    }
    h += ">";
    h += "<p>" + message + "</p>";
    h += "</div></div>";

    if (children.length > 0) {
      h += "<div class=\"comment-thread\">";
      h += display_posts_helper(children);
      h += "</div>";
    }
  }
  return h;
}

function gotComments(serviceName, response) {
  all_comments[serviceName] = add_space_for_children(response);
  redrawComments();
  if (window.location.hash && window.location.hash.length > 0) {
    var s = window.location.hash;
    window.location.hash = "";
    window.location.hash = s;

    var highlighted_comment = document.getElementById(s.replace('#', ''));
    if (highlighted_comment) {
      highlighted_comment.className += " highlighted";
    }
  }
}

function deep_copy(x) {
  return JSON.parse(JSON.stringify(x));
}

function recursively_add_service(c, service) {
  c.push(service);
  var children = c[5];
  for (var i = 0 ; i < children.length ; i++) {
    recursively_add_service(children[i], service);
  }
}

function all_comments_sorted() {
  var ts_comment = [];
  for (var service in all_comments) {
    for (var i = 0 ; i < all_comments[service].length ; i++) {
      var comment_copy = deep_copy(all_comments[service][i]);
      recursively_add_service(comment_copy, service);
      var ts = comment_copy[4];
      ts_comment.push([ts, comment_copy]);
    }
  }
  ts_comment = ts_comment.sort();
  var c = [];
  for (var i = 0 ; i < ts_comment.length ; i++) {
    c.push(ts_comment[i][1]);
  }
  return c;
}

function redrawComments() {
  var d = document.getElementById("comments");
  var h = "<div class=\"comment-thread\">";
  h += display_posts(all_comments_sorted());
  window.acs = all_comments_sorted();
  window.dictionary = dictionary;
  window.quoting = quoting;
  h += "</div>";
  d.innerHTML=h;
}

function pullComments(wsgiUrl, serviceName) {
  ajaxJsonRequest(wsgiUrl.replace("json-comments", "json-comments-cached"), function(response) {
    gotComments(serviceName, response);
    ajaxJsonRequest(wsgiUrl, function(response) {
      gotComments(serviceName, response);
    });
  });
}
</script>''',

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

  'css': '''\
.comment-thread {margin: 0px 0px 0px 30px;}
.content {max-width:550px;}
.comment {max-width: 448px;
          overflow: hidden;
          overflow-wrap: break-word;
          margin-top: 0px;
          margin-bottom: -1px;
          border-top:1px solid black;
          border-bottom:1px solid black;
          padding-top:10px;}
.newcomment { border-left: 1px solid black;
              padding-left: 5px; }
.commentlink {font-style: italic;
              font-size: 80%;
              visibility: hidden;}
.comment:hover .commentlink {visibility: visible}
.highlighted {background-color: lightyellow;}
@media (min-width: 850px) {
  #top-posts { padding-left: 30px;
               position: absolute;
               top: 30px;
               left: 600px;
               max-width: 200px;}}
#title-date-tags { width: 100% }
#wrapper { margin: 8px}
#title-date-tags h3 { margin: 0 }''',

  'amp_boilerplate': '<style amp-boilerplate="">body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-o-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}</style>',

  'amp_noscript_boilerplate': '<noscript><style amp-boilerplate="">body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}</style></noscript>'

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
  self.title,
  config.full_url(self.link()),
  self.day, self.short_month, self.year,
  quote(html))

class Post:
  def __init__(self, slug, date, title, tags, element):
    self.slug = slug
    self.date = date
    self.title = title
    self.published = config.notyet_token not in tags
    tags = [x for x in tags if x != config.notyet_token]
    self.name = title_to_url_component(title)
    self.element = element
    self.updates = {}

    # these are filled in externally for published posts
    self.older_post = None
    self.newer_post = None
    # this is filled in externally for all posts
    self.posts_by_slug = None

    self.month, self.day, self.year = date.split()[1:4]
    self.short_month = self.month[:3]

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
        services.append((2, 'facebook', 'fb', fb_link, token))
      elif service == 'lw':
        lw_link = 'https://lesswrong.com/lw/%s' % token
        services.append((3, 'lesswrong', 'lw', lw_link, token))
      elif service == 'ea':
        ea_link = 'http://effective-altruism.com/ea/%s' % token
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
    self.tags = set(x for x in tags if '/' not in x)

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
          max_width = 95.0
          img.set('style', 'max-width:%.1fvw; max-height:%.1fvw' %
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
    return '\n'.join(self.stringify_(x) for x in element.findall('*'))

  def blog_entry_summary(self):
    element = deepcopy(self.element)
    removing = False
    for child in element.findall('.//*'):
      if child.text and config.break_token in child.text:
        child.text, _ = child.text.split(config.break_token)
        child.text += '%s'
        removing = True
        child.tail = ''
      elif child.tail and config.break_token in child.tail:
        child.tail, _ = child.tail.split(config.break_token)
        child.tail += '%s'
        removing = True
      elif removing:
        child.getparent().remove(child)

    link = config.relative_url(self.link())
    append_more = "%s<a href='%s'>%s...</a>" % (
      ' ' if removing else '<p>', link, 'more' if removing else 'full post')
    html = self.stringify_(element)
    if removing:
      html = html % append_more
    else:
      html = html + append_more

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

    if not self.published:
      element.insert(0, parse('<p><i>draft post</i></p>'))

    amp_styles = set()
    amp_custom_elements = set()

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
          amp_custom_elements.add(
            ('amp-youtube', 'https://cdn.ampproject.org/v0/amp-youtube-0.1.js'))
          iframe.tag = 'amp-youtube'
          videoid, = re.findall('/embed/([^?]*)', iframe.get('src'))
          attrib = iframe.attrib
          width, height = attrib['width'], attrib['height']
          attrib.clear()
          attrib['width'], attrib['height'] = width, height
          attrib['layout'] = 'responsive'
          attrib['data-videoid'] = videoid
        else:
         amp_custom_elements.add(
           ('amp-iframe', 'https://cdn.ampproject.org/v0/amp-iframe-0.1.js'))
         iframe.tag = 'amp-iframe'

         try:
           placeholder_img = iframe.attrib.pop('data-placeholder')
           iframe.append(etree.Element(
             'amp-img', placeholder='', layout='fill', src=placeholder_img))
         except KeyError:
           pass

         iframe.set('sandbox', 'allow-scripts allow-same-origin')

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
      'meta', name='viewport', content=SNIPPETS['meta_viewport']))
    head.append(etree.Element('meta', charset='utf-8'))

    if is_amp:
      head.append(etree.Element(
        'script', async='', src='https://cdn.ampproject.org/v0.js'))

    if is_amp:
      head.append(etree.Element('link', rel='canonical',
                                href=config.relative_url(self.link())))
    #else:
    #  head.append(etree.Element('link', rel='amphtml-draft', href='%s.amp' % (
    #    config.relative_url(self.link()))))

    title = etree.Element('title')
    title.text = self.title
    head.append(title)

    body = etree.Element('body')

    if is_amp:
      amp_custom_elements.add(
        ('amp-analytics', 'https://cdn.ampproject.org/v0/amp-analytics-0.1.js'))
      body.append(parse(SNIPPETS['google_analytics_amp']))
    else:
      head.append(parse(SNIPPETS['google_analytics_nonamp']))


    # TODO: get GA into amp
    # TODO: look into ld json schema for amp

    if is_amp:
      head.append(parse(SNIPPETS['amp_boilerplate']))
      head.append(parse(SNIPPETS['amp_noscript_boilerplate']))

    head.append(parse(
      '<style%s>%s%s</style>' % (
        ' amp-custom=""' if is_amp else '',
        SNIPPETS['css'],
        '\n'.join(sorted(amp_styles)))))

    wrapper = etree.Element('div', id='wrapper')

    wrapper.append(parse(links_partial()))
    wrapper.append(etree.Element('hr'))

    content = etree.Element('div')
    content.set('class', 'content')

    fancy_date = '%s %s, %s' % (self.month, tidy_day(self.day), self.year)

    tag_block = ''
    if self.tags:
      tag_block = '<span>%s</span>' % ', '.join(
        '<i><a href="/news/%s">%s</a></i>' % (tag, tag)
        for tag in self.tags)

    content.append(parse('''<table id="title-date-tags">
    <tr><td valign="top" rowspan="2"><h3><a href="%s">%s</a></h3></td>
        <td align="right" valign="top">%s</td></tr>
    <tr><td align="right" valign="top">%s</td></tr></table>''' % (
      config.relative_url(self.link()), self.title, fancy_date, tag_block)))

    content.append(element)

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

        amp_custom_elements.add((
          'amp-list', 'https://cdn.ampproject.org/v0/amp-list-0.1.js'))
        amp_custom_elements.add((
          'amp-mustache', 'https://cdn.ampproject.org/v0/amp-mustache-0.1.js'))

        comment_thread.append(parse('''
<amp-list width=auto height=500 layout="fixed-height" src=%s>
  <template type="amp-mustache">
    <div class=comment id="{{anchor}}">
      <a dontescapethis="{{source_link}}">{{author}}</a> ({{service}})
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
<script type="text/javascript">
%s
</script>
</div>''' % (
  SNIPPETS['comment_script'],
  '\n'.join(
    "pullComments('/wsgi/json-comments/%s/%s', '%s');\n" % (
      service_abbr, service_tag, service_name)
    for service_name, service_abbr, service_link, service_tag
    in self.services))))

    wrapper.append(content)

    best_posts = [self.posts_by_slug[slug]
                  for slug, _ in random.sample(BEST_POSTS, 5)]

    best_posts_html = '<p>More Posts:</p><ul>%s</ul>' % (
      ''.join('<li><p><a href="%s">%s</a></p></li>' % (
        config.relative_url(other.link()),
        other.title) for other in best_posts))
    for section, other in [('Older Post', self.older_post),
                          ('Newer Post', self.newer_post)]:
      if other:
        best_posts_html = "%s<p>%s:</p><ul><li><p><a href='%s'>%s</a></p></li></ul>" % (
          best_posts_html, section, config.relative_url(other.link()),
          other.title)

    wrapper.append(parse(
      '<div id="top-posts">%s</div>' % best_posts_html))

    wrapper.append(etree.Element('hr'))
    wrapper.append(parse(links_partial()))

    body.append(wrapper)

    page = etree.Element('html', lang='en')
    if is_amp:
      page.set('amp', 'amp')
    page.append(head)
    page.append(body)

    if is_amp:
      for custom_element, custom_element_url in amp_custom_elements:
        ce_script = etree.Element('script', async='', src=custom_element_url)
        ce_script.set('custom-element', custom_element)
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
  self.title,
  config.full_url(self.link()),
  '\n  '.join('<category>%s</category>' % tag
            for tag in sorted(self.tags)),
  self.day, self.short_month, self.year,
  quote(html))

def parse(s):
  return lxml.html.fragment_fromstring(s, create_parent=False)

def parsePosts():
  posts = []
  published_posts = []
  posts_by_name = {}
  posts_by_slug = {}

  with open(config.full_filename(config.in_html)) as inf:
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
        tags_h4 = post_elements[1]
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

        post = Post(slug, date, title, tags, element)
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
  sep = '&#160;&#160;::&#160;&#160;'
  s = sep.join(
    ('<a href="/" rel="author">Jeff Kaufman</a>',
     '<a href="/p/index">Posts</a>',
     '<a href="/news.rss">RSS</a>',
     # can't use rewind symbol because apple makes it ugly
     '<span><a href="__REVERSE_RSS__">&#9666;&#9666;RSS</a>',
     '</span><a href="/contact">Contact</a>'))
  s += '\n'
  return '<div class="headfoot">%s</div>' % s

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

  for tag, tag_posts in tag_to_posts.items():
    if tag == 'all':
      rss_link = '/news.rss'
    else:
      rss_link = '/news/%s.rss' % tag

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
.headfoot { margin: 3px }
h2 { margin: .5em }
body { margin: 0; padding: 0}
li { list-style-type: none; margin: 0 }
li a { display: block; padding: .75em }
li a:link { text-decoration: none }
.title:hover { text-decoration: underline }
ul { margin: 0; padding: 0 }
li:nth-child(odd) {
  background: #EEE;
  background: linear-gradient(to right, #EEE 400px, #FFF 600px);
}
.date { font-size: 85%% ; color: black }
</style>
%s<hr><h2>Posts :: %s (<a href="%s">rss</a>)</h2>
<ul>
%s
</ul>
<hr>%s
</body>
</html>''' % (
  'Blog Posts' if tag == 'all' else 'Posts tagged %s' % tag,
  SNIPPETS['meta_viewport'],
  rss_link,
  SNIPPETS['google_analytics'],
  links_partial(),
  tag,
  rss_link,
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
