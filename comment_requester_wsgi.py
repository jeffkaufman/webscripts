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
import socket

sys.path.append(os.path.dirname(__file__))
from private import *

# Monkey patch to force IPv4, since FB seems to hang on IPv6
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response
            for response in responses
            if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

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

def epoch(timestring):
    return int(time.mktime(
             dateutil.parser.parse(timestring)
                            .astimezone(dateutil.tz.tzlocal())
                            .timetuple()))

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

def flatten(json_comments, parent_key=None):
    flattened = []
    for comment in json_comments:
        ts = comment[4]
        key = '%s %s' % (parent_key, ts) if parent_key else str(ts)
        if len(comment) == 5:
            flattened.append((key, comment))
        elif len(comment) == 6:
            flattened.append((key, comment[:-1]))
            flattened.extend(flatten(comment[-1], key))
        else:
            raise Exception('invalid comment %r' % comment)
    return flattened

def clean_text(s):
    s = re.sub('^(<[^>]*>)*', '', s, re.MULTILINE)
    s = s.replace('<p>', '<br><br>')
    s = s.replace('<br>', '{br}')
    s = re.sub('<[^>]*>', '', s)
    s = s.replace('{br}', '<br>')
    return s

def amp_comments(json_comments):
    return [(key,
             {'author': author,
              'source_link': source_link,
              'anchor': anchor,
              'service': anchor.split('-')[0],
              'text': '%s%s' % ('&rarr;&nbsp;' * key.count(' '),
                                clean_text(text)),
              'timestamp': timestamp})
            for key, (author, source_link, anchor, text, timestamp) in flatten(
                    json_comments)]

def service_archive(service):
    def service_helper(token):
        cwd = os.path.dirname(__file__)
        service_dir = os.path.join(cwd, service + '-comment-archive')
        for leaf in os.listdir(service_dir):
            if leaf.endswith('%s-%s.js' % (service, token)):
                with open(os.path.join(service_dir, leaf)) as inf:
                    return json.loads(inf.read())
        return []
    return service_helper

SERVICE_FNS = {
    'gp': service_archive('gp'),
    'fb': service_archive('fb'),
    'lw': service_lw,
    'ea': service_ea,
    'r': service_r,
    'hn': service_hn}

# actually respond to the request
# raising errors here will give a 500 and put the traceback in the body
def start(environ, start_response):
    path = environ["PATH_INFO"]
    if path.startswith("/wsgi/"):
      path = path[len("/wsgi"):]

    if path.startswith("/json-comments"):
        _, path_initial, service, token = path.split("/", 3)
        
        service_fn = SERVICE_FNS.get(service, None)

        if path_initial == "json-comments-nocache":
            return json.dumps(service_fn(token))

        cache_only = {"json-comments": False,
                      "json-comments-validator": False,
                      "json-comments-cached": True}[path_initial]

        if service_fn:
            response = cacher(cache_only, service_fn, service, token)
            if path_initial == 'json-comments-validator':
                status = '200 OK' if response else '404 Not Found'
                start_response(status, [('content-type', 'text/plain')])
                return ['already started', 'comments: %s' % len(response)]
            return json.dumps(cacher(cache_only, service_fn, service, token))

    elif path == "/amp-json-comments":
        query_string = environ["QUERY_STRING"]
        unsorted_comments = []
        for component in query_string.split('&'):
            service_abbr, service_token = component.split('=')
            if service_abbr not in SERVICE_FNS:
                continue
            unsorted_comments.extend(amp_comments(cacher(
                cache_only=False, fn=SERVICE_FNS[service_abbr],
                service=service_abbr, arg=service_token)))

        start_response('200 OK', [
            ('content-type', 'text/javascript'),
            ('Access-Control-Allow-Origin', '*'),
            ('AMP-Access-Control-Allow-Source-Origin',
             'https://www.jefftk.com'),
            ('Access-Control-Expose-Headers', '*')])
        return ['already started', json.dumps({'items': [
            comment for _, comment in sorted(unsorted_comments)]})]

    start_response('404 Not Found', [('content-type', 'text/plain')])
    return ['already started', 'not supported %r' % path]

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

if __name__ == "__main__":
    server()
