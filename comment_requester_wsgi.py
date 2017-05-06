#!/usr/bin/env python
import cgi
import traceback
import re
import urllib
import urllib2
import math
import json
import os
import sys
import time
import dateutil.parser
import Cookie
import subprocess
import base64
from xml.dom import minidom
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from private import *

def unescape(s):
    return (s.replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&quot;', '"')
            .replace('&amp;', '&'))

def slurp(url, data=None, headers={}, timeout=60):
    identifier = "Jeff Kaufman"
    botname = "cross-comment"
    if "reddit" in url:
        identifier = "/u/cbr"
    elif "lesswrong" in url:
        identifier = "/user/jkaufman"
    if 'User-Agent' not in headers:
        headers['User-Agent'] = '%s bot by %s (www.jefftk.com)' % (botname, identifier)

    response = urllib2.urlopen(urllib2.Request(url, data, headers), None, timeout)
    return response.read()

# Google is using something that is almost, but not quite, json.  So take a strong from G+
# and turn it into json so we can use the json parser
#  - the string starts with ')]}' for no reason I can tell
#  - in lists they use missing values instead of null
#    - [1,] instead of [1,null] etc
#  - in dictionaries they use unquoted numeric keys
#    - {12345: "foo"} instead of {"12345": "foo"}
def gplus_loads(s):
    if s.startswith(")]}'"):
        s = s[len(")]}'"):]
    for f,r in [(",,", ",null,"),
                ("[,", "[null,"),
                (",]", ",null]"),
                ("\n", "")]:
        while f in s:
            s = s.replace(f,r)
    s = re.sub('{([0-9]+):', '{"\\1":', s)

    try:
        return json.loads(s)
    except ValueError:
        print s
        raise

# I wrote the g+ code later, so it's properly object oriented.  This is only for g+.
class Comment(object):
    def __init__(self, raw):
        self.user_id = raw[6]
        assert self.user_id == raw[25][1]
        self.user = raw[25][0]

        message = []
        for message_segment in raw[27][-1]:
            if message_segment[0] == 0:
                # some text
                message.append(escape(message_segment[1].replace(u"\ufeff", "")))
            elif message_segment[0] == 1:
                # newline
                message.append("<br>")
            elif message_segment[0] == 2:
                # link
                link = message_segment[3][0]
                message.append('<a href="%s">%s</a>' % (escape(link), escape(link)))
            elif message_segment[0] == 3:
                # tag
                user_link = "https://plus.google.com/%s" % escape(message_segment[4][1])
                message.append('@<a href="%s">%s</a>' % (
                    user_link, sanitize_name(message_segment[1])))
            elif message_segment[0] == 4:
                # hashtag
                # don't bother linking
                message.append(escape(message_segment[1]))
            else:
                import pprint
                pprint.pprint(raw)
                raise Exception("unknown message type %s" % message_segment[0])
        self.message = "\n".join(message)

        self.anchor = raw[3]
        self.ts = raw[3]/1000

    def user_link(self):
        return "https://plus.google.com/%s" % self.user_id

# This is also only for g+
class Post(object):
    def __init__(self, user_id, post_id):
        fullurl = 'https://plus.google.com/_/stream/getactivity/%s?updateId=%s' % (
            user_id, post_id)

        r = gplus_loads(slurp(fullurl))
        assert len(r) >= 1

        r = r[0]

        assert r[0] == "os.u"
        assert len(r) == 2

        self.comments = []
        for comment_raw in r[1][7]:
            self.comments.append(Comment(comment_raw))

        self.link = "https://plus.google.com/%s/posts/%s" % (user_id, post_id)

def die500(start_response, e):
    trb = "%s: %s\n\n%s" % (e.__class__.__name__, e, traceback.format_exc())

    start_response('500 Internal Server Error', [('content-type', 'text/plain')])
    #return ""
    return trb

def escape(s):
    s = unicode(s)
    for f,r in [["&", "&amp;"],
                ["<", "&lt;"],
                [">", "&gt;"]]:
        s = s.replace(f,r)
    return s


def refresh_token_helper(refresh_token, client_id, client_secret):
    token_url = "https://accounts.google.com/o/oauth2/token"
    post_body = urllib.urlencode({
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token"})
    j = json.loads(slurp(token_url, post_body))
    return j["access_token"]


def anl_refresh_token():
    return refresh_token_helper(
        refresh_token=A_REFRESH_TOKEN,
        client_id=A_CLIENT_ID,
        client_secret=A_CLIENT_SECRET)

def lat_refresh_token():
    return refresh_token_helper(
        refresh_token=L_REFRESH_TOKEN,
        client_id=L_CLIENT_ID,
        client_secret=L_CLIENT_SECRET)

def sanitize_names_extended(comments, raw_names):
    for a, b in INITIALS.items(): raw_names[a] = b

    for comment in comments:
        for raw_name, sanitized_name in raw_names.items():
            comment[3] = comment[3].replace(raw_name, sanitized_name)
            if raw_name in comment[3]:
                print raw_name
            if len(comment) > 5 and comment[5]:
                comment[5] = sanitize_names_extended(comment[5], raw_names)
    return comments

def service_gp(gpid):
    p = Post(GP_POSTER_ID, gpid)
    raw_names = {}
    out = []
    for comment in p.comments:
        out.append([sanitize_name(comment.user),
                    comment.user_link(),
                    "gp-%s" % comment.anchor,
                    "<p>%s</p>" % comment.message,
                    comment.ts])
        raw_names[comment.user] = sanitize_name(comment.user)
    return sanitize_names_extended(out, raw_names)


def epoch(timestring):
    return int(time.mktime(
             dateutil.parser.parse(timestring)
                            .astimezone(dateutil.tz.tzlocal())
                            .timetuple()))

def sanitize_name(name):
    name = INITIALS.get(name, name)
    name = name.split()[0]
    return name

def service_fb(objid):
    if not objid.startswith("4102153_"):
        objid = "4102153_" + objid

    def collect_comments(url):
        response = json.loads(slurp(url))
        if "data" not in response or not response["data"]:
            return []
        data = response["data"]
        if "paging" in response and "next" in response["paging"]:
            data.extend(collect_comments(response["paging"]["next"]))
        return data

    # debug with https://www.jefftk.com/p/conversation-with-gleb-of-intentional-insights#fb-805642967912_805768436472
    def resolve_replies(comments):
        for comment in comments:
            if "comments" in comment:
                response = comment["comments"]
                if "paging" in response and "next" in response["paging"]:
                    response["data"].extend(collect_comments(response["paging"]["next"]))

    # could do up to &limit=80 here, but following next= links is better
    fullurl = "%s/%s/comments?access_token=%s&fields=created_time,from,message,id,comments" % (
        "https://graph.facebook.com/v2.8", objid, FB_CODE)
    comments = collect_comments(fullurl)
    resolve_replies(comments)

    def anchor(comment):
        return escape(comment["id"])

    def user_id(comment):
        return escape(comment["from"]["id"])

    def skip(comment):
        return str(user_id(comment)) in FB_SHOW_BLACKLIST

    def raw_name(comment):
        return comment["from"]["name"]

    def name(comment):
        return sanitize_name(raw_name(comment))

    def message(comment):
        return escape(comment["message"]).replace("\n\n", "\n<p>")

    def comment_id(comment):
        return anchor(comment).split("_")[-1]

    def user_link(comment):
        if str(user_id(comment)) in FB_LINK_BLACKLIST:
            return '#'
        return "https://www.facebook.com/%s/posts/%s?comment_id=%s" % (
            FB_POSTER_ID, objid.split("_")[-1], comment_id(comment))
        # return "https://www.facebook.com/profile.php?id=%s" % user_id(comment)

    def ts(comment):
        return epoch(comment['created_time'])

    out = []
    raw_names = {}

    def to_list(comment):
        raw_names[raw_name(comment)] = name(comment)
        return [name(comment),
                user_link(comment),
                "fb-%s" % anchor(comment),
                message(comment),
                ts(comment),
                []] # replies

    for comment in comments:
        if not skip(comment):
            l = to_list(comment)
            if "comments" in comment:
                for reply in comment["comments"]["data"]:
                    if not skip(reply):
                        l[-1].append(to_list(reply))
            out.append(l)
    return sanitize_names_extended(out, raw_names)

def parse_reddit_style_json_comment(raw_comment, url):
    raw_comment = raw_comment["data"]

    if raw_comment["replies"]:
        children_raw_list = raw_comment["replies"]["data"]["children"]
        children = [parse_reddit_style_json_comment(child_raw, url)
                    for child_raw in children_raw_list]
    else:
        children = []

    return [unescape(raw_comment["author"]),
            "%s#%s" %(re.sub(r"\.json$", "", url), raw_comment["id"]),
            "r-%s" % raw_comment["id"],
            unescape(raw_comment["body_html"]).replace("<a href=", "<a rel=nofollow href="),
            int(raw_comment["created_utc"]),
            children]

def pull_reddit_style_json(url):
    # returns nested comments
    j = json.loads(slurp(url))

    if len(j) < 2:
        return []

    raw_comments = j[1]["data"]["children"]
    return [parse_reddit_style_json_comment(raw_comment, url)
            for raw_comment in raw_comments]

BEGIN_HN_COMMENT='<span class="comment">'
END_HN_COMMENT="</span>"
def pull_hn_comments(url):
  html = slurp(url).split("\n")

  comments = []

  current_indent = 0
  comment_so_far = []
  in_comment = False
  prevous_line = ""
  for line in html:
    line = line.strip().replace("</span></div><br>", "")

    indentations = re.findall(
        '<img src="s.gif" height="1" width="([0-9]+)">', line)
    if indentations:
        indentation = indentations[-1]

    if line.startswith(BEGIN_HN_COMMENT):
      assert not in_comment
      in_comment = True
      line = line.replace(BEGIN_HN_COMMENT, "")

      if indentation is not None:
        current_indent = int(indentation)

        assert current_indent % 40 == 0
        current_indent = current_indent / 40
      else:
        current_indent = 0

      potential_user_info = []
      for a_matcher in ["([^<]*)", "<font[^>]*>([^<]*)</font>"]:
        potential_user_info = re.findall(
          '<a href="[^"]*">%s</a> <a href="([^"]*)">([\\d]*) (year|day|hour|minute|second)s? ago</a>' % a_matcher, previous_line)
        if potential_user_info:
           username, link_suffix, time_ago, time_units = potential_user_info[0]
           break
      if not potential_user_info:
        print previous_line
        raise Exception

    if in_comment:
      if END_HN_COMMENT not in line:
        comment_so_far.append(line)
      else:
        in_comment = False
        comment_so_far.append(line.split(END_HN_COMMENT)[0])

        comments.append((current_indent, "\n".join(comment_so_far), username, time_ago, time_units, link_suffix))
        comment_so_far = []
    previous_line = line

  threaded_comments = []
  for indent, comment, username, time_ago, time_units, link_suffix in comments:
    append_to = threaded_comments
    for i in range(indent):
      # find the last comment in the list, prepare to append to its comment section
      append_to = append_to[-1][-1]
    append_to.append([
        username,
        "https://news.ycombinator.com/%s" % link_suffix,
        link_suffix.split("=")[-1],
        comment,
        timedelta_to_epoch(int(time_ago), time_units),
        []])
  return threaded_comments

def timedelta_to_epoch(time_ago, time_units):
  unit_table = {"second": 0,
                "minute": 1,
                "hour": 2,
                "day": 3,
                "year": 4}
  unit = unit_table[time_units]
  if unit >= unit_table["minute"]:
    time_ago *= 60
  if unit >= unit_table["hour"]:
    time_ago *= 60
  if unit >= unit_table["day"]:
    time_ago *= 24
  if unit >= unit_table["day"]:
    time_ago *= 24
  if unit >= unit_table["year"]:
    time_ago *= 365

  return int(time.time())-time_ago

def pull_reddit_style_rss(url):
    def pull_tag(item, tag):
        m = re.match(".*<%s>([^<]*)</%s>.*" % (tag, tag), item)
        if not m:
            return "%s missing" % tag
        return m.groups()[0].strip()

    def title(item):
        return pull_tag(item, 'title')

    def author(item, main_title):
        t = title(item)
        a = t.split()[0]
        title_guess = "%s on %s" % (a, main_title)

        if title_guess != t:
            return "Author not understood"
        return a

    def link(item):
        return pull_tag(item, 'link')

    def anchor(item):
        return link(item).split("/")[-1]

    def fix_links(d):
        return re.sub(r'\[([^\]]+)\]\(([^\)]+)\)',
                      r'<a rel="nofollow" href="\2">\1</a>', d)

    def description(item):
        d = unescape(pull_tag(item, 'description'))
        return fix_links(d)

    def ts(item):
        return epoch(pull_tag(item, 'dc:date'))

    items = slurp(url).replace('\n','').split('<item>')
    if not items:
        return []

    del items[0] # description, header junk
    if not items:
        return []

    article = items[0]
    main_title = title(article)
    del items[0]
    if not items:
        return []

    return [(unescape(author(item, main_title)),
             unescape(link(item)),
             anchor(item),
             description(item),
             ts(item))
            for item in items]

def service_lw(token):
    m = re.match('^[a-zA-Z0-9]+$', token)
    if not m:
        return []

    url = "http://lesswrong.com/lw/%s.rss" % token
    return pull_reddit_style_rss(url)

def service_ea(token):
    m = re.match('^[a-zA-Z0-9]+$', token)
    if not m:
        return []

    url = "http://effective-altruism.com/ea/%s.rss" % token
    return pull_reddit_style_rss(url)

def service_r(token):
    m = re.match('^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', token)
    if not m:
        return []

    subreddit, post_id = token.split('/')

    url = "http://www.reddit.com/r/%s/comments/%s.json" % (subreddit, post_id)
    return pull_reddit_style_json(url)

def service_hn(token):
  url = "https://news.ycombinator.com/item?id=%s" % token
  return pull_hn_comments(url)

def cacher(cache_only, fn, service, arg):
    import memcache
    import time

    mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    key = "%s/%s" % (service, arg)
    value = mc.get(key)
    t = 0
    fn_value = []
    if value:
        t, fn_value = json.loads(value)

    if cache_only:
        return fn_value

    # cache is still fresh
    if time.time()-t < 5*60:
        return fn_value

    # check the filesystem
    this_dir = os.path.dirname(os.path.abspath(__file__))
    assert service.isalnum()
    service_dir = os.path.join(this_dir, "comment-archive", service)
    if not os.path.exists(service_dir):
        os.mkdir(service_dir)
    no_slash_arg = arg.replace("/", "_")
    assert no_slash_arg.replace("_","").isalnum()
    archive_fn = os.path.join(service_dir, no_slash_arg + ".json")
    if os.path.exists(archive_fn):
        with open(archive_fn) as inf:
            fn_value = json.loads(inf.read())
    else:
        # Fall back to pulling from the service.  Ideally we could
        # serve stale data while kicking off a background thread, but
        # we're not that sophisticated.
        fn_value = fn(arg)

        # Save a backup.  We don't use these, but they'll be nice to
        # have if something goes wrong.
        if fn_value:  # Don't bother saving [].
            with open(archive_fn + ".save", "w") as outf:
                outf.write(json.dumps(fn_value))
                outf.write("\n")

    mc.set(key, json.dumps([time.time(), fn_value]))

    return fn_value

# actually respond to the request
# raising errors here will give a 500 and put the traceback in the body
def start(environ, start_response):
    path = environ["PATH_INFO"]
    if path.startswith("/wsgi/"):
      path = path[len("/wsgi"):]

    if path.startswith("/json-comments"):
        _, path_initial, service, token = path.split("/", 3)
        service_fn = None
        if service == "gp":
            service_fn = service_gp
        elif service == "fb":
            service_fn = service_fb
        elif service == "lw":
            service_fn = service_lw
        elif service == "ea":
            service_fn = service_ea
        elif service == "r":
            service_fn = service_r
        elif service == "hn":
            service_fn = service_hn

        if path_initial == "json-comments-nocache":
            return json.dumps(service_fn(token))

        cache_only = {"json-comments": False,
                      "json-comments-cached": True}[path_initial]

        if service_fn:
            return json.dumps(cacher(cache_only, service_fn, service, token))

    return "not supported"


def application(environ, start_response):
    raw = False
    try:
        output = start(environ, start_response)
        code = None
        if output is None:
            output = ''
        if type(output) == type([]):
          code, output = output
        if code == "already started":
          pass # nothing needs doing
        elif code == "html":
          start_response('200 OK', [('content-type', 'text/html')])
        elif code == "htmlraw":
          start_response('200 OK', [('content-type', 'text/html')])
          raw = True
        else:
          start_response('200 OK', [('content-type', 'text/javascript')])
    except Exception, e:
        output = die500(start_response, e)

    if not raw:
        output = output.encode('utf8')

    return (output, )

def server():
    from wsgiref.simple_server import make_server

    # run on port 8010
    make_server('',8010,application).serve_forever()

def recalculate_fb_token():
    redirect_url = "http://www.jefftk.com/"

    print "We need to regenerate a long-lived access token for facebook"
    print "Load the following URL in your browser:"
    url = ("https://www.facebook.com/dialog/oauth?"
           "client_id=%s"
           "&scope=public_profile,basic_info,user_posts,user_managed_groups,user_friends"
           "&redirect_uri=%s") % (FB_APP_ID, redirect_url)
    print " ", url
    print "paste the full url it redirects you to press enter"
    r = raw_input("> ")
    fb_code = re.findall('code=([^#]*)#_=_$', r)[0]

    def slurp_access_token(url):
        r = urllib2.urlopen(urllib2.Request(url)).read()
        return dict(x.split('=') for x in r.split('&'))['access_token']

    short_lived_token = slurp_access_token(
        "https://graph.facebook.com/oauth/access_token?"
        "client_id=%s"
        "&redirect_uri=%s"
        "&client_secret=%s"
        "&code=%s" % (FB_APP_ID, redirect_url, FB_APP_SECRET, fb_code))

    long_lived_token = slurp_access_token(
        "https://graph.facebook.com/oauth/access_token?"
        "client_id=%s&"
        "client_secret=%s&"
        "grant_type=fb_exchange_token&"
        "fb_exchange_token=%s" % (FB_APP_ID, FB_APP_SECRET, short_lived_token))

    print "Set:"
    print "  FB_CODE='%s'" % long_lived_token

    print "Then restart uwsgi: sudo service uwsgi restart"

if __name__ == "__main__":
    {"server": server,
     "fbtoken": recalculate_fb_token}[sys.argv[1]]()
