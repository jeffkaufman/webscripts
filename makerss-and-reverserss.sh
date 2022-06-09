#!/bin/bash
RSS_SOURCES="
  -s https://apenwarr.ca/log/rss.php
  -s https://www.benkuhn.net/index.xml
  -s https://danluu.com/post/atom.xml
  -s https://juliawise.net/feed/
  -s https://sideways-view.com/feed/
  -s https://www.lilywise.com/posts.rss
  -s https://www.annawise.net/posts.rss
  -s https://cullenokeefe.com/blog?format=rss"

/home/jefftk/code/webscripts/makerss.py && echo "rss made" && \
  /home/jefftk/bin/reverserss.py && echo "done"

/home/jefftk/code/openring/openring \
  $RSS_SOURCES \
  < /home/jefftk/code/openring/in-small.html \
  | sed 's~https://danluu.com/post/atom/index.xml~https://danluu.com~g' \
  > /home/jefftk/jtk/current-openring.html && \
/home/jefftk/code/openring/openring \
  -n 100 -p 5 -l 500 $RSS_SOURCES \
  < /home/jefftk/code/openring/in-big.html \
  | sed 's~https://danluu.com/post/atom/index.xml~https://danluu.com~g' \
  > /home/jefftk/jtk/ring.html
