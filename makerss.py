#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
usage:

  python makerss.py

This was much less 'designed' than 'accreted', and generally makes me sad
to work on.  But it does what I want it to, so I haven't felt the need to
replace it.

"""

import sys, os, re, random, shutil, stat

SITE_URL="https://www.jefftk.com"
SITE_DIR="/home/jefftk/jtk"
IN_HTML="%s/news_raw.html" % SITE_DIR
FRONT_PAGE="%s/index.html" % SITE_DIR
FRONT_PAGE_TMP=FRONT_PAGE+"~"
OUT_DIR="%s/news" % SITE_DIR
P_DIR="%s/p" % SITE_DIR
NEW_OUT_DIR="%s/news-new" % SITE_DIR
NEW_P_DIR="%s/p-new" % SITE_DIR
PREV_OUT_DIR="%s/news-prev" % SITE_DIR
PREV_P_DIR="%s/p-prev" % SITE_DIR
P_URL="/p"
RSS_URL="%s/news.rss" % SITE_URL
RSS_FNAME="%s/news.rss" % SITE_DIR

RSS_FULL_FNAME="%s/news_full.rss" % SITE_DIR

RSS_MAX = 30
FRONT_PAGE_MAX=6 # how many to show on the front page

GP_UID="103013777355236494008"

def meta_viewport(n):
  return '<meta name="viewport" content="width=%spx">' % n

COMMENT_SCRIPT = r"""
<script type="text/javascript">
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
</script>
"""

def edit_front_page(front_page_list):
  outf = open(FRONT_PAGE_TMP, "w")
  inf = open(FRONT_PAGE, "r")

  skipping = False
  for line in inf:
    if "<!-- end recent thoughts -->" in line:
      for entry in front_page_list:
        outf.write("\n".join(entry))
        outf.write("\n")
      skipping = False

    if not skipping:
      outf.write(line)

    if "<!-- begin recent thoughts -->" in line:
      skipping = True

  assert not skipping

  outf.close()
  inf.close()

  os.rename(FRONT_PAGE_TMP, FRONT_PAGE)

def quote(s):
  return s.replace("&", "&amp;").replace("<","&lt;").replace(">", "&gt;").replace('"', '&quot;')

def write_header(w, d=None):
  w('<?xml version="1.0" encoding="ISO-8859-1" ?>')
  w('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
  w('')
  w('  <channel>')
  w('    <atom:link href="%s" rel="self" type="application/rss+xml" />' % RSS_URL)
  w("    <title>Jeff Kaufman's Writing</title>")
  w("    <link>http://www.jefftk.com/news/</link>")
  w("    <description>Jeff Kaufman's Writing</description>")
  w("    <language>en-us</language>")

def write_footer(w):
  w("  </channel>")
  w("</rss>")

ITEM_RE = re.compile(r'<a name="([^"]*)"></a><h3>([^:]*):</h3>')
TITLE_RE = re.compile(r'<h3>([^>]*)</h3>')
TAGS_RE = re.compile(r'<h4>Tags:([^>]*)</h4>')

def items(s):

  cur_item = []

  found_title = False

  def sendout():
    if not found_title:
      cur_item.append("untitled")
    cur_item.append("".join(cur_text))
    cur_item.append(set(cur_tags))
    x = cur_item[:]

    del cur_item[:]
    del cur_text[:]
    del cur_tags[:]

    return x

  cur_text = []
  cur_tags = []
  for line in s:

    match = ITEM_RE.search(line)
    if match:
      if cur_item:
        yield sendout()
        found_title = False

      link_anchor, date = match.groups()
      cur_item.append(link_anchor)
      cur_item.append(date)

    elif not cur_item:
      pass

    else:
      if not found_title:
        match = TITLE_RE.search(line)
        if match:
          cur_item.append(match.groups()[0])
          found_title = True
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

def title_to_url_component(s):
  s = s.lower()
  s = s.replace("'", "").replace('"', "")
  s = re.sub("[^A-Za-z0-9]", "-", s)
  s = re.sub("-+", "-", s)
  s = re.sub("^-*", "", s)
  s = re.sub("-*$", "", s)
  return s

def make_link(pretty_name):
  return "%s/%s" % (P_URL, pretty_name)

updates = []

pretty_names = {}
titles = {}
title_and_link = []
title_and_link_index = {}
with open(IN_HTML) as inf:
  for n, (link_anchor, date, title, raw_text, tags) \
        in enumerate(items(open(IN_HTML))):
    pretty_name = title_to_url_component(title)

    if pretty_name in titles:
      raise Exception("'%s' for %s turns to %s which is a duplicate" % (
          title, link_anchor, pretty_name))
    titles[pretty_name] = 1
    pretty_names[link_anchor] = pretty_name
    if "notyet" not in tags:
      title_and_link_index[n] = len(title_and_link)
      title_and_link.append((
        title, "%s/%s" % (P_URL, pretty_name)))

    for match in re.findall(r'<b>Update \d\d\d\d-\d\d-\d\d</b>.{0,300}',
                            raw_text, re.DOTALL):

      update_slug, = re.match(r'<b>Update (\d\d\d\d-\d\d-\d\d)</b>',
                              match).groups()
      update_anchor = 'update-%s' % update_slug

      beginning, end = match.split('</b>', 1)

      end_short = end.split('<p>')[0].split('</div>')[0]

      update_text = beginning + '</b>' + end_short + '...'

      update_link = '%s#%s' % (make_link(pretty_name), update_anchor)

      updates.append((update_slug, update_link, update_text))

updates.sort(reverse=True)

def best_posts(earlier, later):
  best = [
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
    #('2011-08-07', 'Contra Dance Calling With Lights'),
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
    #('2009-09-29', 'The \'Expand This Here\' Operator'),
    # ('2009-03-11', 'Introducing icdiff'),
    ]

  random.shuffle(best)

  li_html = '<li style="margin-bottom: 0.5em;">'

  best_posts_html = '<p>More Posts:</p><ul>%s</ul>' % (
    "".join('%s<a href="%s/%s">%s</a>' % (
        li_html, P_URL, pretty_names[post_date], post_title)
            for (post_date, post_title) in random.sample(best,5)))

  for section, info in [("Older Post", earlier),
                        ("Newer Post", later)]:
    if info:
      title, link = info
      best_posts_html = "%s<p>%s:</p><ul>%s<a href='%s'>%s</a></ul>" % (
        best_posts_html, section, li_html, link, title)

  return best_posts_html


def links_partial():
  sep = '&nbsp;&nbsp;::&nbsp;&nbsp;'
  s = sep.join(
    ('<a href="/" rel="author">Jeff Kaufman</a>',
     '<a href="/p/index">Posts</a>',
     '<a href="/news.rss">RSS</a>',
     # can't use rewind symbol because apple makes it ugly
     '<span><a href="__REVERSE_RSS__">&#9666;&#9666;RSS</a>',
     '</span><a href="/contact">Contact</a>'))
  s += "\n"
  return "<div class=headfoot>%s</div>" % s

def write_links_footer(p):
    p.write("  <hr>\n")
    p.write(links_partial())
    p.write('  </body></html>\n')

def write_rss_item_begin(n, w_partial, w_full, title, link, tags):
  for w in [w_partial, w_full]:
    if w == w_partial and n >= RSS_MAX:
      continue

    w('    <item>')
    w('      <guid>%s</guid>' % link)
    w("      <title>%s</title>" % title)
    w("      <link>%s%s</link>" % (SITE_URL,link))
    for tag in sorted(tags):
      w("      <category>%s</category>" % tag)

def write_rss_item_end(n, w_partial, w_full, day, month, year, t):
  for w in [w_partial, w_full]:
    if w == w_partial and n >= RSS_MAX:
      continue

    w("      <pubDate>%s %s %s 08:00:00 EST</pubDate>" % (day, month[:3], year))
    w("      <description>%s</description>" % quote(t))
    w("    </item>")

def start():
  rss_out=open(RSS_FNAME, "w")
  rss_full_out=open(RSS_FULL_FNAME, "w")

  def w_partial(s):
    rss_out.write(s + "\n")
  def w_full(s):
    rss_full_out.write(s + "\n")

  # delete old staging dirs
  for d in [NEW_OUT_DIR, NEW_P_DIR, PREV_OUT_DIR, PREV_P_DIR]:
    if os.path.exists(d):
      shutil.rmtree(d)
  os.mkdir(NEW_OUT_DIR)
  os.mkdir(NEW_P_DIR)

  write_header(w_partial)
  write_header(w_full)

  for updates_n, (update_slug, update_link, update_text) in enumerate(updates):
    write_rss_item_begin(updates_n, w_partial, w_full,
                         'Update %s' % update_slug,
                         update_link, ['update_rss'])
    write_rss_item_end(updates_n, w_partial, w_full,
                       update_slug, '', '', update_text)

  css = ('<style type="text/css">'
         'img {width: 100%}'
         '.comment-thread {margin: 0px 0px 0px 30px;}'
         '.content {max-width:550px;}'
         '.comment {max-width: 448px;'
         '          overflow: hidden;'
         '          overflow-wrap: break-word;'
         '          margin-top: 0px;'
         '          margin-bottom: -1px;'
         '          border-top:1px solid black;'
         '          border-bottom:1px solid black;'
         '          padding-top:10px;}'
         '.newcomment { border-left: 1px solid black;'
         '              padding-left: 5px; }'
         '.commentlink {font-style: italic;'
         '              font-size: 80%;'
         '              visibility: hidden;}'
         '.comment:hover .commentlink {visibility: visible}'
         '.highlighted {background-color: lightyellow;}'
         '@media (min-width: 850px) {'
         '  #top-posts { padding-left: 30px;'
         '               position: absolute;'
         '               top: 30px;'
         '               left: 600px;'
         '               max-width: 200px;}}'
         '#title-date-tags { width: 100% }'
         '</style>')

  tag_to_items = {}

  front_page_list = []

  all_posts = items(open(IN_HTML))

  prev_pretty_name=""
  cur_pretty_name=""
  printed_most_recent=False

  for n, (link_anchor, date, title, raw_text, tags) \
      in enumerate(all_posts):
    prev_pretty_name = cur_pretty_name
    cur_pretty_name=pretty_names[link_anchor]
    link = make_link(cur_pretty_name)

    for (f, r) in [("’", "'"),
                   ("‘", "'"),
                   ('“', '"'),
                   ('”', '"')]:
      raw_text = raw_text.replace(f, r)

    raw_text = re.sub(r'<b>Update (\d\d\d\d-\d\d-\d\d)</b>',
                      r'<a name="update-\1"></a><b>Update \1</b>',
                      raw_text)

    new_raw_text = []
    for line in raw_text.split("\n"):
      if "<img src=" in line:
        matches = re.findall('<img src="([^"]*)"', line)
        if len(matches) == 1:
          oldlink = matches[0]
          if oldlink.startswith("/"):
            fname, ext = oldlink.rsplit(".", 1)
            if ext in ["jpg", "png"]:
              srcsets = []
              for sizing in ["2x", "3x", "4x"]:
                newlink = "%s-%s.%s" % (fname, sizing, ext)
                for suffix in ["-sm", "-small", "-tn", "-1x"]:
                  if fname.endswith(suffix):
                    newlink = "%s-%s.%s" % (fname[:-len(suffix)], sizing, ext)
                newlink_ondisk = "%s%s" % (SITE_DIR, newlink)
                if os.path.exists(newlink_ondisk):
                  srcsets.append("%s %s" % (newlink, sizing))
                  #print "  %s %s" % (newlink, sizing)
              if srcsets:
                srcset = ", ".join(srcsets)
                #print "using %s as srcset for %s" % (srcset, oldlink)
                line = line.replace(oldlink, '%s" srcset="%s' % (oldlink, srcset))
      new_raw_text.append(line)
    raw_text = "\n".join(new_raw_text)

    if "~~break~~" in raw_text:
      beginning_text, ending_text = raw_text.split("~~break~~")
      broke_text = True
    else:
      beginning_text = raw_text
      ending_text = ""
      broke_text = False

    text = "%s%s" % (beginning_text, ending_text)

    beginning_text = re.sub('<a href=[^>]*><img src=',
                            '<a href="' + link + '"><img src=',
                            beginning_text)

    notyet = "notyet" in tags
    if notyet:
      tags.remove("notyet")
    elif not printed_most_recent:
      # print the last pretty name in a notyet post
      # assumes all notyet posts preceed all real posts
      print "http://www.jefftk.com/p/%s" % prev_pretty_name
      printed_most_recent = True

    services = []
    for tag in tags:
      if '/' not in tag:
        continue
      token = tag.split("/", 1)[1]
      if tag.startswith('g+/'):
        services.append((1, "google plus", "gp", 'https://plus.google.com/%s/posts/%s' % (GP_UID, token), token))
      elif tag.startswith('fb/'):
        if token.startswith("note/"):
          token = token.replace("note/","")
          fb_link = "https://www.facebook.com/note.php?note_id=%s" % token
        else:
          token = token.replace("status/", "")
          fb_link = "https://www.facebook.com/jefftk/posts/%s" % token.split("_")[-1]
        services.append((2, "facebook", "fb", fb_link, token))
      elif tag.startswith('lw/'):
        lw_link = "http://lesswrong.com/lw/%s" % token
        services.append((3, "lesswrong", "lw", lw_link, token))
      elif tag.startswith('ea/'):
        ea_link = "http://effective-altruism.com/ea/%s" % token
        services.append((4, "the EA Forum", "ea", ea_link, token))
      elif tag.startswith('r/'):
        subreddit, post_id = token.split('/')
        r_link = "http://www.reddit.com/r/%s/comments/%s" % (subreddit, post_id)
        services.append((5, "r/%s" % subreddit, "r", r_link, token))
      elif tag.startswith('hn/'):
        services.append((6, "hacker news", "hn", 'https://news.ycombinator.com/item?id=%s' % token, token))

    # sort by and then strip off priorities
    services = [x[1:] for x in sorted(services)]

    tags = set(x for x in tags if '/' not in x)

    no_tags_no_ws = re.sub('<[^>]*>', '', re.sub('\s+',' ',re.sub('<style>[^<]*</style>','',text))).strip()
    meta = ('<meta name="description" content="%s..." />' % quote(no_tags_no_ws[:400]) + " " +
            '<meta name="keywords" content="%s" />' % quote(', '.join(tags)) + " " +
            meta_viewport("device-width, initial-scale=1"))

    text = "<p>" + text

    tag_block = ""
    if tags:
      tag_block = ", ".join(
        '<i><a href="/news/%s">%s</a></i>' % (tag, tag)
        for tag in tags)

    if services:
      comments_links = ", ".join('<a href="%s">%s</a>' % (service_link, service_name)
                                 for (service_name, _, service_link, _) in services)
      rss_comments_note = "<p><i>Comment via: %s</i>" % comments_links
    else:
      rss_comments_note = ""

    if not notyet:
      write_rss_item_begin(n, w_partial, w_full, title, link, tags)

    month, day, year = date.split()[1:4]

    if not notyet:
      t = text + rss_comments_note
      write_rss_item_end(n, w_partial, w_full, day, month, year, t)

    if notyet:
      text = "<i>draft post</i><p>%s" % text

    date_number_file = os.path.join(NEW_OUT_DIR, link_anchor + ".html")
    pretty_name_file = os.path.join(NEW_P_DIR,
                                    cur_pretty_name + ".html")
    per_file = open(date_number_file, "w")

    per_file.write("<html>\n")
    per_file.write("<head><title>%s</title>%s%s</head>\n" % (title, meta, css))

    per_file.write('<body>%s</div><hr><div class="content">' % links_partial())
    per_file.write('<table id=title-date-tags>')
    per_file.write('<tr><td valign=top rowspan=2><h3><a href="%s">%s</a></h3>' % (
      link, title))
    fancy_date = "%s %s, %s" % (month, tidy_day(day), year)
    per_file.write('    <td align=right valign=top>%s' % fancy_date)
    per_file.write('<tr><td align=right valign=top>%s</table>' % tag_block)
    per_file.write(text)

    if services:
      per_file.write("<p>Comment via: %s\n" % (
          ', '.join('<a href="%s">%s</a>' % (service_link, service_name)
                    for service_name, service_abbr, service_link, service_tag in services)))
      per_file.write('<div id="comments">')
      per_file.write(COMMENT_SCRIPT)
      per_file.write('<script type="text/javascript">')
      for service_name, service_abbr, service_link, service_tag in services:
        per_file.write("pullComments('/wsgi/json-comments/%s/%s', '%s');\n" % (
            service_abbr, service_tag, service_name))
      per_file.write('</script>')
      per_file.write('</div>')

    earlier, later = None, None
    if n in title_and_link_index:
      i = title_and_link_index[n]
      if i+1 < len(title_and_link):
        earlier = title_and_link[i+1]
      if i-1 >= 0:
        later = title_and_link[i-1]
    per_file.write("<div id=top-posts>%s</div>" % best_posts(earlier, later))

    write_links_footer(per_file)
    per_file.close()

    shutil.copy(date_number_file, pretty_name_file)
    st = os.stat(date_number_file)
    os.chmod(date_number_file, st.st_mode & (stat.S_IRUSR | stat.S_IWUSR))

    if not notyet and len(front_page_list) < FRONT_PAGE_MAX:
      blog_entry_summary = []
      w = blog_entry_summary.append
      w("<div class=blog-entry-summary>")
      w("<div class=blog-entry-date><a class=invisible-link href='%s'>" % link)
      w("%s %s, %s" % (month, tidy_day(day), year))
      w("</a></div>")
      w("<div class=blog-entry-title><a class=invisible-link href='%s'>%s</a></div>" % (link, title))
      w("<div class=blog-entry-beginning>")
      w("<p>")
      w(beginning_text)

      if broke_text:
        w(" <a href='%s'>more...</a>" % link)
      else:
        w("<p><a href='%s'>full post...</a>" % link)

      w("</div>")
      w("</div>")
      front_page_list.append(blog_entry_summary)

    tags.add("all")
    for tag in tags:
      if tag not in tag_to_items:
        tag_to_items[tag] = []
      if not notyet:
        tag_to_items[tag].append((year, month, day, link, title))


  for tag, item_list in tag_to_items.items():
    if tag == "all":
      rss_link = "/news.rss"
    else:
      rss_link = "/news/%s.rss" % tag
    rss_link_tag = '<link rel=alternate type="application/rss+xml" title="RSS Feed" href="%s">' % rss_link

    t = open(os.path.join(NEW_OUT_DIR, "%s.html" % tag), "w").write
    t("<html>\n")
    if tag == "all":
      page_title = "Blog Posts"
    else:
      page_title = "Posts tagged %s" % tag

    t("  <head><title>%s</title>%s%s</head>\n" % (
      page_title, meta_viewport("device-width, initial-scale=1"), rss_link_tag))
    t('<style>'
      '.headfoot { margin: 3px }'
      'h2 { margin: .5em }'
      'body { margin: 0; padding: 0}'
      'li { list-style-type: none; margin: 0 }'
      'li a { display: block; padding: .75em }'
      'li a:link { text-decoration: none }'
      '.title:hover { text-decoration: underline }'
      'ul { margin: 0; padding: 0 }'
      'li:nth-child(odd) {'
      '  background: #EEE;'
      '  background: linear-gradient(to right, #EEE 400px, #FFF 600px);'
      '}'
      '.date { font-size: 85% ; color: black }'
      '</style>')

    t('  <body>%s<hr><h2>Posts :: %s (<a href="%s">rss</a>)</h2>\n' % (
      links_partial(), tag, rss_link))
    t('  <ul>')
    for year, month, day, link, title in item_list:
      t('   <li><a href="%s">'
        '       <div class=title>%s</div>'
        '       <div class=date>%s %s, %s</div></a></li>\n' % (
        link, title, month, day, year))
    t('  </ul>\n')
    t('  <hr>%s\n' % links_partial())
    t('  </body>\n')
    t('</html>\n')

  write_footer(w_full)
  write_footer(w_partial)

  edit_front_page(front_page_list)

  os.rename(P_DIR, PREV_P_DIR)
  os.rename(NEW_P_DIR, P_DIR)

  os.rename(OUT_DIR, PREV_OUT_DIR)
  os.rename(NEW_OUT_DIR, OUT_DIR)

  os.symlink("%s/all.html" % OUT_DIR, "%s/index.html" % OUT_DIR)
  os.symlink("%s/all.html" % OUT_DIR, "%s/index.html" % P_DIR)

def tidy_day(day):
  d = str(int(day))
  suffix = "th"
  if len(d) == 2 and d[0] == '1':
    suffix = "th"
  elif d[-1] == '1':
    suffix = "st"
  elif d[-1] == '2':
    suffix = "nd"
  elif d[-1] == '3':
    suffix = "rd"
  return d + suffix

if __name__ == "__main__":
  start()
