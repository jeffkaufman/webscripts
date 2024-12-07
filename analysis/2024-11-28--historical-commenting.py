#!/usr/bin/env python3

import os
import json
from collections import Counter

selected_services = set()
with open("dated_comment_services.json") as inf:
    for slug, services in sorted(json.load(inf).items()):
        for service, token in services:
            if service in ["fb", "gp", "lw", "m"]:
                selected_services.add(service)

selected_services = list(sorted(selected_services))

def count_recursively(comments):
    n = 0
    for comment in comments:
        n += 1
        if type(comment[-1]) == type([]):
            n += count_recursively(comment[-1])
    return n

def count_comments(service, token):
    fname = "comment-archive/%s/%s.json.save" % (
        service, token.replace("/", "_"))
    if not os.path.exists(fname):
        return 0

    n = 0
    with open(fname) as inf:
        n += count_recursively(json.load(inf))

    return n

monthly_counts = Counter()
monthly_posts = Counter()

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

        month = "%s-%s" % (y, m)
        monthly_posts[month] += 1

        for (service, token) in services:
            count_service = service
            if service == "m1":
                count_service = "m"
            
            monthly_counts[month, count_service] += count_comments(
                service, token)

if False:
    print("month", *selected_services, sep="\t")
    for month, n_monthly_posts in sorted(monthly_posts.items()):
        print(month,
              *[monthly_counts[month, service]
                for service in selected_services],
              sep="\t")
elif True:
    print("month", *selected_services, sep="\t")
    for month, n_monthly_posts in sorted(monthly_posts.items()):
        print(month,
              *[monthly_counts[month, service]/monthly_posts[month]
                for service in selected_services],
              sep="\t")
else:
    print("month", "posts", sep="\t")
    for month, n_monthly_posts in sorted(monthly_posts.items()):
        print(month, n_monthly_posts, sep="\t")
