These are some scripts for manipulating my website

They're probably only useful to others as examples; they're pretty
tied to the layout of my site.

Licensing: GNU GPL 2 or later

## Usage

### proc_schedule.py (obsolete)

python proc_schedule.py view
 - shows a pretty table of upcoming events

proc_schedule.py add
 - add an event

proc_schedule.py ical
 - update the ical feed
 - might want to call this after manual editing or running add

In general add is just for convenience; if you need to edit you should
open it up in a text editor

### makerss.py

This was named when all it did was make an rss feed.  Now it also
builds a large number of static html pages.

python makerss.py
 - updates rss feed
 - updates public_html/news/

### comment_requester_wsgi.py (obsolete)

Run this as wsgi.  It needs a facebook app created for it, and it will
only pull comments from your user account.  To get a token use:

    python comment_requester_wsgi.py fbtoken

The other half of this is included as javascript on each of my blog
posts.  To see the latest of that, visit:

    https://www.jefftk.com/p/conversation-with-gleb-of-intentional-insights?PageSpeed=off

And look down to the script that begins after <div id="comments">

## Server Setup

To migrate to a new server:

1. Get a new VPS.  Make sure there's enough disk space for growth.  Do
   this early, since they may take some time to verify identity and
   provision. Write down root password.

1. Add entry for new server to `~/.ssh/config` locally

1. ssh in as root

```
adduser jefftk
sudo usermod -aG sudo jefftk

visudo
# append jefftk ALL=(ALL) NOPASSWD:ALL

su jefftk -
cd
mkdir .ssh

nano -w .ssh/authorized_keys
# add contents of local `~/.ssh/id_rsa.pub`

ssh-keygen -t ed25519 -C jeff@jefftk.com

# Add contents of remote `~/.ssh/id_ed25519.pub` to old server's
# `~/.ssh/authorized_keys`

rsync -rta www.jefftk.com:/home/jefftk /home/jefftk

sudo apt install emacs nginx sox ffmpeg flake8 g++ gcc git icdiff \
     imagemagick lame mosh make nginx-extras python3 screen tmux uwsgi \
     uwsgi-plugin-python3 whois wget certbot python3-pip memcached \
     libimage-exiftool-perl

sudo python3 -m pip install python-dateutil
sudo python3 -m pip install pymemcache

cd /var
sudo mkdir www-aw www-bd www-fc www-bts www-fr www-kf www-lw \
   www-nh www-nw www-oc www-rs www-test www-tc
sudo chown -R jefftk www*

for x in www www-aw www-bd www-fc www-bts www-fr www-kf www-lw \
     www-nh www-nw www-oc www-rs www-test www-tc ; do
  rsync -rta www.jefftk.com:/var/$x/ /var/$x/
done

cd

scp www.jefftk.com:/etc/nginx/nginx.conf .
sudo mv nginx.conf /etc/nginx/nginx.conf
sudo mv  /etc/nginx/nginx.conf /etc/nginx/conf.d/
scp www.jefftk.com:/usr/local/nginx/conf/nginx.redirects.conf .
sudo mv nginx.redirects.conf /etc/nginx/
# on old server: sudo tar -czvf le.tgz /etc/letsencrypt/
scp www.jefftk.com:le.tgz .
tar -xvzf le.tgz
sudo mv etc/letsencrypt/* /etc/letsencrypt/
sudo systemctl enable nginx
sudo systemctl daemon-reload
sudo service nginx start

scp www.jefftk.com:/etc/systemd/system/uwsgi* .
sudo mv uwsgi-* /etc/systemd/system/

sudo systemctl enable uwsgi-comments
sudo systemctl enable uwsgi-simplechat
sudo systemctl enable uwsgi-echo-01
sudo systemctl enable uwsgi-echo-02

sudo systemctl enable memcached
sudo service memcached start
sudo service uwsgi-comments start
sudo service uwsgi-simplechat start
sudo service uwsgi-echo-01 start
sudo service uwsgi-echo-02 start
```

1. verify everything works with /etc/hosts overrides

1. switch dns over

1. wait 1+ weeks before taking down the old server


