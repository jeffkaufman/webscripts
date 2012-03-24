#!/usr/bin/env python
import traceback
import re
import urllib
import urllib2
import json

# your email address goes here
EMAIL="user@example.com"

# comments by these user ids will not show up
SHOW_BLACKLIST=["12345", "67890"]

# comments by these user ids will not link back to that person's profile
LINK_BLACKLIST=["23456", "78901"]

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
        self.user_id = raw[6]

# This is also only for g+
class Post(object):
    def __init__(self, user_id, post_id):
        fullurl = 'https://plus.google.com/_/stream/getactivity/%s?updateId=%s' % (
            user_id, post_id)

        r = gplus_loads(urllib2.urlopen(urllib2.Request(fullurl)).read())
        assert len(r) == 1
        r = r[0]

        assert r[0] == "os.u"
        assert len(r) == 2

        self.comments = []
        for comment_raw in r[1][7]:
            self.comments.append(Comment(comment_raw))

        self.link = "https://plus.google.com/%s/posts/%s" % (user_id, post_id)

# facebook offline access token.  You get this with oauth, and it's complicated.  It's
# also being deprecated starting 2012-05-01:
#    https://developers.facebook.com/roadmap/offline-access-removal/
# auth docs: https://developers.facebook.com/docs/authentication/
#
CODE= get a facebook token

# for me these are 'jefftk' and '103013777355236494008' respectively
FB_POSTER_ID= your post info for facebook
GP_POSTER_ID= your post info for google plus

def die500(start_response, e):
    trb = "%s: %s\n\n%s" % (e.__class__.__name__, e, traceback.format_exc())
    print trb

    start_response('500 Internal Server Error', [('content-type', 'text/plain')])
    return ""

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
            s.append('<a href="%s">%s</a>:' % (
                    user_link, comment.user))
            s.append("<p>%s</p>" % comment.message)

        s.append('</blockquote>')

    return s, p.link

def fbcomments(objtype, objid):
    fullurl = "%s/%s/comments?access_token=%s" % (
        "https://graph.facebook.com/", objid, CODE)
    response = json.loads(urllib2.urlopen(urllib2.Request(fullurl)).read())

    if objtype == "note":
        post_link = "https://www.facebook.com/note.php?note_id=%s" % objid
    elif objtype == "status":
        post_link = "https://www.facebook.com/%s/posts/%s" % (FB_POSTER_ID, objid)
    else:
        assert False

    s = []

    if "data" in response and response["data"]:

        s.append('Comments on <a href="%s">facebook</a>:' % post_link)
        s.append('<blockquote>')
        for comment in response["data"]:
            name = escape(comment["from"]["name"])
            user_id=escape(comment["from"]["id"])

            if str(user_id) in SHOW_BLACKLIST:
                continue
            elif str(user_id) in LINK_BLACKLIST:
                user_link = "#"
            else:
                user_link = "https://www.facebook.com/profile.php?id=%s" % user_id

            s.append("<hr>")
            s.append('<a href="%s">%s</a>:' % (user_link, name))

            s.append("<p>%s</p>" % escape(comment["message"]).replace("\n\n", "\n<p>"))

        s.append('</blockquote>')

    return s, post_link


# actually respond to the request
# raising errors here will give a 500 and put the traceback in the body
def start(environ, start_response):
    path = environ["PATH_INFO"]
    if path.startswith("/comments/"):
        m = re.match("^/comments/([a-z]+)/([0-9]+)(/[A-Za-z0-9]+)?$", environ["PATH_INFO"])
        if m:
            objtype, objid, gpid = m.groups()
            if gpid:
                gpid = gpid.replace("/", "")

            if objtype in ["note", "status"]:
                return comments(objtype, objid, gpid)

    return "usage: /comments/[note|status]/[fbgraphid]/[g+id]"

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
