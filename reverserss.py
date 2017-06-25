#!/usr/bin/env python
FEED_POSTS = 5
import re
import os

def back_from(post_number):
    return "back_from_%s.rss" % post_number

def rss_from(post_number):
    return "/home/jefftk/jtk/news/%s" % back_from(post_number)

def posts_for(posts, post_number):
    current_post = len(posts) - 1

    include_before = max(0, 2*post_number - current_post)
    include_to = max(0, include_before - FEED_POSTS)

    return reversed(posts[include_to:include_before])

def write_post(posts, post_number, header, footer):
    with open(rss_from(post_number), "w") as outf:
        header = header.replace(
            "Blog Posts",
            "Blog Posts back from post %s" % post_number)
        header = header.replace(
            "</description>",
            " from post %s back</description>" % post_number)
        header = header.replace(
            '<atom:link href="http://www.jefftk.com/news.rss"',
            '<atom:link href="http://www.jefftk.com/news/%s"' % back_from(post_number))
        outf.write(header)
        outf.writelines(posts_for(posts, post_number))
        outf.write(footer)

def post_slug(post):
    try:
        slug, = re.findall("<link>.*/p/([^<]+)</link>", post)
    except Exception:
        print repr(post)
        raise
    return slug

def edit_in_reverse_rss_link(post_number, current_number, post_slug):
    n = int(max(0, current_number - .5*(current_number-post_number)))

    fname = "/home/jefftk/jtk/p/%s.html" % post_slug
    with open(fname) as inf:
        post = "".join(inf.readlines())
    post = post.replace("__REVERSE_RSS__",
                        "http://www.jefftk.com/news/back_from_%s.rss" % n)
    with open(fname, "w") as outf:
        outf.write(post)

def cateogrize_header(header, category, full):
    header = header.replace(
        "Blog Posts",
        "Blog Posts on %s" % category)
    header = header.replace(
        "</description>",
        " on %s</description>" % category)
    header = header.replace(
        '<atom:link href="http://www.jefftk.com/news.rss"',
        '<atom:link href="http://www.jefftk.com/news/%s%s.rss"' % (
            category,
            "_full" if full else ""))
    return header

def write_category_feeds(header, posts, footer):
    category_counts = {} # category -> int
    for post in posts:
      categories = re.findall("<category>([^>]*)</category>", post)
      for category in categories:
        fname = "/home/jefftk/jtk/news/%s.rss" % category
        fname_full = "/home/jefftk/jtk/news/%s_full.rss" % category
        is_new = category not in category_counts

        with open(fname, "w" if is_new else "a") as outf:
          with open(fname_full, "w" if is_new else "a") as outf_full:
            if is_new:
              category_counts[category] = 0
              # TODO: make header substitutions
              outf.write(cateogrize_header(header, category, full=False))
              outf_full.write(cateogrize_header(header, category, full=True))
            if category_counts[category] < 10:
              outf.write(post)
            outf_full.write(post)
            category_counts[category] += 1
    for category in category_counts:
      fname = "/home/jefftk/jtk/news/%s.rss" % category
      fname_full = "/home/jefftk/jtk/news/%s_full.rss" % category
      with open(fname, "a") as outf:
        outf.write(footer)
      with open(fname_full, "a") as outf_full:
        outf_full.write(footer)

def start():
    header = []
    posts = []
    current_post = []
    footer = []

    with open("/home/jefftk/jtk/news_full.rss") as inf:
        for line in inf:
            if "</channel>" in line or footer:
                footer.append(line)
                continue

            if "<item>" not in line and not current_post:
                header.append(line)
                continue

            current_post.append(line)

            if "</item>" in line:
                posts.append("".join(current_post))
                current_post = []

    write_category_feeds("".join(header), posts, "".join(footer))

    posts.reverse()

    for post_number in range(len(posts)):
        write_post(posts, post_number, "".join(header), "".join(footer))

    for post_number, post in enumerate(posts):
        edit_in_reverse_rss_link(post_number, len(posts)-1, post_slug(post))

    def replace_in_file(fname_long):
        if fname_long.endswith(".html") and os.path.isfile(fname_long):
            with open(fname_long) as inf:
                contents = inf.read()
            contents = contents.replace("__REVERSE_RSS__",
                                        "/news/2013-02-08")
            with open(fname_long, "w") as outf:
                outf.write(contents)

    for fname in os.listdir("/home/jefftk/jtk/p/"):
        replace_in_file("/home/jefftk/jtk/p/%s" % fname)
    for fname in os.listdir("/home/jefftk/jtk/news/"):
        replace_in_file("/home/jefftk/jtk/news/%s" % fname)

if __name__ == "__main__":
    start()
