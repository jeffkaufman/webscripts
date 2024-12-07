#!/usr/bin/env python3

import os
import json
from collections import Counter

authors = Counter()
def count_authors(comments):
    for comment in comments:
        authors[comment[0]] += 1
        if type(comment[-1]) == type([]):
            count_authors(comment[-1])

def count_comments(service, token):
    fname = "comment-archive/%s/%s.json.save" % (
        service, token.replace("/", "_"))
    if not os.path.exists(fname):
        return 0

    with open(fname) as inf:
        count_authors(json.load(inf))

with open("dated_comment_services.json") as inf:
    for slug, services in sorted(json.load(inf).items()):
        y, m, d = slug.replace(
            "-a", "").replace(
                "-b", "").replace(
                    "a", "").replace(
                        "b", "").replace(
                            "2020-03-066", "2020-03-06").split("-")

        m = m.zfill(2)
        d = d.zfill(2)

        date = "%s-%s-%s" % (y, m, d)

        if date >= "2012-02-19":
            continue
        
        for (service, token) in services:
            if service != "gp":
                continue
            
            count_comments(service, token)

import pprint
pprint.pprint(authors)
