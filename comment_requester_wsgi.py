#!/usr/bin/env python
import cgi
import traceback
import re
import urllib.request, urllib.parse, urllib.error
import math
import json
import os
import sys
import time
import dateutil.parser
import http.cookies
import subprocess
import base64
from collections import defaultdict
import socket
import html
from html.parser import HTMLParser

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
    elif "schelling.pt" in url:
        identifier = "@jefftk@schelling.pt"

    if 'User-Agent' not in headers:
        headers['User-Agent'] = '%s bot by %s (www.jefftk.com)' % (botname, identifier)

    response = urllib.request.urlopen(urllib.request.Request(url, data, headers), None, timeout)
    return response.read().decode("utf-8")

def die500(start_response, e):
    trb = "%s: %s\n\n%s" % (e.__class__.__name__, e, traceback.format_exc())

    start_response('500 Internal Server Error', [('content-type', 'text/plain')])
    #return ""
    return trb

def escape(s):
    s = str(s)
    for f,r in [["&", "&amp;"],
                ["<", "&lt;"],
                [">", "&gt;"]]:
        s = s.replace(f,r)
    return s


def refresh_token_helper(refresh_token, client_id, client_secret):
    token_url = "https://accounts.google.com/o/oauth2/token"
    post_body = urllib.parse.urlencode({
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


class HnHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state = "initial"
        self.comments = []
        self.current_text = []

    def get_attr(self, attrs, key):
        for k, v in attrs:
            if k == key:
                return v
        return None

    def has_class(self, attrs, cls):
        value = self.get_attr(attrs, "class")
        return value and cls in value

    def handle_starttag(self, tag, attrs):
        if self.state == "initial" and tag == "table" and self.has_class(attrs, "comment-tree"):
            self.state = "comments"
        elif self.state == "comments" and tag == "tr" and self.has_class(attrs, "comtr"):
            self.current_id = self.get_attr(attrs, "id")
            self.state = "need-indent"
        elif self.state == "need-indent" and tag == "img":
            self.current_indent = self.get_attr(attrs, "width")
            self.state = "need-user"
        elif self.state == "need-user" and tag == "a" and self.has_class(attrs, "hnuser"):
            self.current_user_link = self.get_attr(attrs, "href")
            self.state = "need-user-name"
        elif self.state == "need-age-a" and tag == "a":
            self.state = "need-age-text"
        elif self.state == "need-comment-div" and tag == "div" and self.has_class(attrs, "comment"):
            self.state = "need-comment"
            self.current_text = ""
        elif self.state == "need-comment" and tag == "i":
            self.current_text += " <i>"
        elif self.state == "need-comment" and tag == "a":
            self.current_text += ' <a href="%s">' % html.escape(self.get_attr(attrs, "href"), quote=True)
        elif self.state == "need-comment" and tag == "p":
            self.current_text += "<p>"
        elif self.state == "need-comment" and tag == "div":
            self.current_indent = int(self.current_indent)
            if self.current_indent % 40 != 0:
                raise RuntimeException("bad hn indent: %s" % self.current_indent)

            self.current_indent = self.current_indent // 40

            self.comments.append((self.current_indent,
                                  self.current_id,
                                  self.current_user_link,
                                  self.current_user_name,
                                  self.current_age,
                                  self.current_text))
            self.current_text = ""
            self.state = "comments"


    def handle_endtag(self, tag):
        if self.state == "need-comment" and tag == "i":
            self.current_text += "</i> "
        elif self.state == "need-comment" and tag == "a":
            self.current_text += "</a> "

    def handle_data(self, data):
        if self.state == "need-user-name":
            self.current_user_name = data
            self.state = "need-age-a"
        elif self.state == "need-age-text":
            self.current_age = data
            self.state = "need-comment-div"
        elif self.state == "need-comment":
            data = data.strip()
            if data:
                self.current_text += html.escape(data, quote=True)

def pull_hn_comments(url):
  parser = HnHtmlParser()
  parser.feed(slurp(url))

  threaded_comments = []
  for indent, current_id, user_link, user_name, age, text in parser.comments:
      (time_ago, time_units), = re.findall("^([\\d]*) (year|day|hour|minute|second)s? ago$", age)

      append_to = threaded_comments
      for i in range(indent):
          # find the last comment in the list, prepare to append to its comment section
          append_to = append_to[-1][-1]
      append_to.append([
          user_name,
          "https://news.ycombinator.com/item?id=%s" % current_id,
          "hn-%s" % current_id,
          text,
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

def gather_children(comments_with_parent_ids, root_id=None):
    root = []
    for comment_id, comment in list(comments_with_parent_ids.items()):
        parent_id = comment[-1]
        if parent_id and parent_id != root_id:
            parent = comments_with_parent_ids[parent_id][-2]  # -2 is children
        else:
            parent = root
        parent.append(comment)
    for comment in list(comments_with_parent_ids.values()):
        del comment[-1]  # remove temporary parent_id
    return root

def lw_style_service(token, service, domain):
    if token.startswith('posts/'):
        token = token[len('posts/'):]

    m = re.match('^[a-zA-Z0-9]+$', token)
    if not m:
        return []

    post_body = '{"query": "{comments(input: { terms: { view: \\"postCommentsOld\\", postId: \\"%s\\", }}) { results { _id postedAt author parentCommentId contents { html }}}}"}' % token
    response = json.loads(slurp(
        "%s/graphql" % domain,
        data=post_body.encode("utf-8"),
        headers={'Content-Type': 'application/json'}))

    comments = {}
    for comment in response['data']['comments']['results']:
        # output format:
        #   username
        #   permalink
        #   comment id (derived from link)
        #   comment_html
        #   timestamp
        #   children
        #   parent_id (temporary)
        comments[comment["_id"]] = [
            comment["author"],
            "%s/posts/%s#%s" % (domain, token, comment["_id"]),
            "%s-%s" % (service, comment["_id"]),
            comment["contents"]["html"],
            epoch(comment["postedAt"]),
            [],
            comment["parentCommentId"]]

    return gather_children(comments)

class HTMLToTextConverter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

def strip_tags(untrusted_html):
    converter = HTMLToTextConverter()
    converter.feed(untrusted_html)
    return converter.text

def service_m(token):
    if not re.match('^[0-9]+$', token):
        return []

    url = "https://schelling.pt/api/v1/statuses/%s/context" % token
    response = json.loads(slurp(url))

    comments = {} # id -> comment array

    for child in response["descendants"]:
        username = escape(child["account"]["display_name"])
        permalink = escape(child["url"])
        comment_id = escape(child["id"])
        timestamp = epoch(child["created_at"])
        comment_html = strip_tags(child["content"])
        children = []
        parent_id = escape(child["in_reply_to_id"])  # temporary

        comments[comment_id] = [
            username, permalink, comment_id, timestamp,
            comment_html, children, parent_id]

    return gather_children(comments, token)

def service_lw(token):
    return lw_style_service(token, 'lw', 'https://www.lesswrong.com')

def service_ea(token):
    return lw_style_service(token, 'ea', 'https://forum.effectivealtruism.org')

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
    from pymemcache.client.base import Client
    import time

    mc = Client('127.0.0.1:11211')

    key = "%s/%s" % (service, arg)
    value = mc.get(key)
    t = 0
    fn_value = []
    if value:
        if type(value) == type(b''):
            value = value.decode('utf-8')
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
        if token.startswith("note/"):
            token = token[len("note/"):]
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
    'm': service_m,
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
    except Exception as e:
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
