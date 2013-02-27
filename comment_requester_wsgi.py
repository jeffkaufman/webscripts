#!/usr/bin/env python
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
sys.path.append(os.path.dirname(__file__))

# This pulls in user-specific data.  Some examples:
#
# FB_POSTER_ID="jefftk"
# GP_POSTER_ID="103013777355236494008"
#
# FB_CODE = get this from oauth for offline access.  Doesn't need any special permissions.
from private import *

def unescape(s):
    return (s.replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&quot;', '"')
            .replace('&amp;', '&'))

def slurp(url, data=None, headers={}):
    identifier = "Jeff Kaufman"
    if "reddit" in url:
        identifier = "/u/cbr"
    elif "lesswrong" in url:
        identifier = "/user/jkaufman"
    headers['User-Agent'] = 'cross-comment bot by %s (www.jefftk.com)' % identifier
    return urllib2.urlopen(urllib2.Request(url, data, headers)).read()

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
        self.user = raw[1]
        self.message = raw[2]
        self.anchor = raw[3]
        self.ts = raw[3]/1000
        self.user_id = raw[6]

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

def comments(objtype, objid, gpid):
    s = []

    if gpid:
        c, gplink = gpcomments(gpid)
        s.extend(c)
    else:
        gplink = None

    c, fblink = fbcomments(objtype, objid)
    s.extend(c)

    comment_request = '<a href="%s">facebook</a>' % fblink
    if gplink:
        comment_request = '<a href="%s">google plus</a>, %s,' % (gplink, comment_request)

    s.append('<br>Comment on %s or write %s<br>' % (comment_request, EMAIL))
    return 'document.write(%s);' % json.dumps("\n".join(s))

def gpcomments(gpid):
    p = Post(GP_POSTER_ID, gpid)
    s = []

    if p.comments:
        s.append('Comments on <a href="%s">google plus</a>:' % p.link)
        s.append('<blockquote>')
        for comment in p.comments:
            user_link = "https://plus.google.com/%s" % comment.user_id

            s.append("<hr>")
            s.append('<a name="gp-%s" href="%s">%s</a>:' % (
                    comment.anchor, user_link, comment.user))
            s.append("<p>%s</p>" % comment.message)

        s.append('</blockquote>')

    return s, p.link

def fbcomments(objtype, objid):
    if objtype == "note":
        post_link = "https://www.facebook.com/note.php?note_id=%s" % objid
    elif objtype == "status":
        post_link = "https://www.facebook.com/%s/posts/%s" % (FB_POSTER_ID, objid)
    else:
        assert False

    fullurl = "%s/%s/comments?access_token=%s" % (
        "https://graph.facebook.com/", objid, FB_CODE)
    response = json.loads(slurp(fullurl))

    s = []

    if "data" in response and response["data"]:

        s.append('Comments on <a href="%s">facebook</a>:' % post_link)
        s.append('<blockquote>')
        for comment in response["data"]:
            name = escape(comment["from"]["name"])
            user_id=escape(comment["from"]["id"])
            anchor=escape(comment["id"])

            if str(user_id) in FB_SHOW_BLACKLIST:
                continue
            elif str(user_id) in FB_LINK_BLACKLIST:
                user_link = "#"
            else:
                user_link = "https://www.facebook.com/profile.php?id=%s" % user_id

            s.append("<hr>")
            s.append('<a name="fb-%s" href="%s">%s</a>:' % (anchor, user_link, name))

            s.append("<p>%s</p>" % escape(comment["message"]).replace("\n\n", "\n<p>"))

        s.append('</blockquote>')

    return s, post_link

# There's also stuff in here for pulling data from google analytics,
# which I don't use any more, and latitude, which I do.

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

def current_location(key):
    url = 'https://www.googleapis.com/latitude/v1/currentLocation?granularity=best'
    headers = { "Authorization": "OAuth " + key }

    j = json.loads(slurp(url, None, headers))
    d = j["data"]
    assert d["kind"] == "latitude#location"
    return d["latitude"], d["longitude"]

def distance(p1, p2):
    lat_1, lon_1 = p1
    lat_2, lon_2 = p2

    lat_1, lon_1 = math.radians(float(lat_1)), math.radians(float(lon_1))
    lat_2, lon_2 = math.radians(float(lat_2)), math.radians(float(lon_2))

    r = 3963 # radius of the earth in miles
    return math.acos(math.sin(lat_1)*math.sin(lat_2) +
                     math.cos(lat_1)*math.cos(lat_2)*math.cos(lon_1-lon_2))*r

def city(lat, lon, distance_from_home):
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false" % (
        lat, lon)
    j = json.loads(urllib2.urlopen(url).read())
    assert j["status"] == "OK"

    ac = j["results"][0]["address_components"]

    city = None
    state = None
    for a in ac:
        if 'locality' in a["types"]:
            city = a["short_name"]
        elif 'administrative_area_level_1' in a["types"]:
            state = a["short_name"]

    if city:
        if distance_from_home < 50:
            return city
        else:
            return "%s %s" % (city, state)

    raise Exception("none found")

def neat_location(lat, lon):
    distances = [(distance(k_loc, (lat, lon)), k_name)
                 for (k_name, k_loc) in KNOWN_LOCATIONS.items()]
    distances.sort()

    best_distance, best_name = distances[0]

    if best_distance < 0.25:
        return best_name

    try:
        return city(lat, lon, distance(KNOWN_LOCATIONS['Home'], (lat, lon)))
    except Exception:
        pass

    return "somewhere unknown"

def location(s):
    access_token = lat_refresh_token()
    current_latlon = current_location(access_token)

    if s == "raw":
        return unsupported # "%s, %s" % current_latlon
    elif s == "plain":
        return neat_location(*current_latlon)
    elif s == "neat":
        map_url=MAP_URL

        txt = '<a href="%s">%s</a> (via GPS)' % (
            map_url, neat_location(*current_latlon))
        return "document.getElementById('location').innerHTML = %s;" % json.dumps(txt)

    return "Unknown request for location '%s'" % s

def service_gp(gpid):
    p = Post(GP_POSTER_ID, gpid)
    return [(comment.user,
             comment.user_link(),
             "gp-%s" % comment.anchor,
             "<p>%s</p>" % comment.message,
             comment.ts)
            for comment in p.comments]

def epoch(timestring):
    return int(time.mktime(
             dateutil.parser.parse(timestring)
                            .astimezone(dateutil.tz.tzlocal())
                            .timetuple()))

def service_fb(objid):
    fullurl = "%s/%s/comments?access_token=%s&limit=80" % (
        "https://graph.facebook.com/", objid, FB_CODE)
    response = json.loads(slurp(fullurl))

    def anchor(comment):
        return escape(comment["id"])

    def user_id(comment):
        return escape(comment["from"]["id"])

    def skip(comment):
        return str(user_id(comment)) in FB_SHOW_BLACKLIST

    def name(comment):
        return comment["from"]["name"]

    def message(comment):
        return escape(comment["message"]).replace("\n\n", "\n<p>")

    def comment_id(comment):
        return anchor(comment).split("_")[-1]

    def user_link(comment):
        if str(user_id(comment)) in FB_LINK_BLACKLIST:
            return '#'
        return "https://www.facebook.com/%s/posts/%s?comment_id=%s" % (
            FB_POSTER_ID, objid, comment_id(comment))
        # return "https://www.facebook.com/profile.php?id=%s" % user_id(comment)

    if "data" not in response or not response["data"]:
        return []

    def ts(comment):
        return epoch(comment['created_time'])

    return [(name(comment),
             user_link(comment),
             "fb-%s" % anchor(comment),
             message(comment),
             ts(comment))
            for comment in response["data"]
            if not skip(comment)]

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

def service_r(token):
    m = re.match('^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', token)
    if not m:
        return []

    subreddit, post_id = token.split('/')

    url = "http://www.reddit.com/r/%s/comments/%s.json" % (subreddit, post_id)
    return pull_reddit_style_json(url)

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

    # cache for 5min
    if time.time()-t > 5*60:
        fn_value = fn(arg)
        mc.set(key, json.dumps([time.time(), fn_value]))

    # ideally we could serve stale data while kicking off a background
    # thread, but we're not that sophisticated.
    return fn_value

# actually respond to the request
# raising errors here will give a 500 and put the traceback in the body
def start(environ, start_response):
    path = environ["PATH_INFO"]
    if path.startswith("/comments/"):
        # old-style requests, probably could delete this now
        m = re.match("^/comments/([a-z]+)/([0-9]+)(/[A-Za-z0-9]+)?$", path)
        if m:
            objtype, objid, gpid = m.groups()
            if gpid:
                gpid = gpid.replace("/", "")

            if objtype in ["note", "status"]:
                return comments(objtype, objid, gpid)
    elif path.startswith("/json-comments"):
        _, path_initial, service, token = path.split("/", 3)
        service_fn = None
        if service == "gp":
            service_fn = service_gp
        elif service == "fb":
            service_fn = service_fb
        elif service == "lw":
            service_fn = service_lw
        elif service == "r":
            service_fn = service_r

        cache_only = {"json-comments": False,
                      "json-comments-cached": True}[path_initial]

        if service_fn:
            return json.dumps(cacher(cache_only, service_fn, service, token))
    elif path.startswith("/location/"):
        return location(path.replace("/location/",""))
    elif path.startswith("/pageviews"):
        return most_viewed_posts()

    return "\n".join(("usage:",
                      "  /comments/[note|status]/[fbgraphid]/[g+id]",
                      "  /json-comments/service/service-token",
                      "  /location/raw",
                      "  /location/neat",
                      ))


#   sets up db cursor, wraps some error checking, runs start
def application(environ, start_response):
    try:
        output = start(environ, start_response)
        if output is None:
            output = ''
        start_response('200 OK', [('content-type', 'text/javascript')])
    except Exception, e:
        output = die500(start_response, e)

    return (output.encode('utf8'), )

# if we're run on our own, run as a server
#   see server.sh for the wrapping
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    import paste.reloader

    # whenever this file or its imports change, paste.reloader will
    # make us exit so our wrapper can restart us
    paste.reloader.install()

    # run on port 8010
    make_server('',8010,application).serve_forever()
