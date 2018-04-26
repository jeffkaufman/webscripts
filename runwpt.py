# Run WebPageTest against an example url to get the tokens we need to
# make requests directly.

import re
import os
import json
import time
import urllib.parse
import urllib.request

def localfname(x):
  return os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

def fetch_json(url):
  return json.loads(urllib.request.urlopen(url).read().decode('utf8'))

def start():
  with open(localfname('wptkey.txt')) as inf:
    key = inf.read().strip()
  keys = {
    'url': 'https://www.facebook.com/jefftk/posts/938839471052',
    'runs': '1',
    'fvonly': '1',
    'script':
      'navigate https://www.facebook.com/jefftk/posts/938839471052\n'
      'clickAndWait data-comment-prelude-ref=action_link_bling',
    'f': 'json',
    'k': key,
    'noimages': '1',
    'htmlbody': '1',
    'noopt': '1',
  }
  r = fetch_json('http://www.webpagetest.org/runtest.php?%s' % (
    '&'.join('%s=%s' % (k, urllib.parse.quote(v)) for (k, v) in keys.items())))
  assert r['statusCode'] == 200
  jsonUrl = r['data']['jsonUrl']
  for i in range(200):
    time.sleep(5)
    r = fetch_json(jsonUrl)
    statusCode = r['statusCode'] if 'statusCode' in r else r['data']['statusCode']
    if 100 <= statusCode < 200:
      import pprint
      pprint.pprint(r)
      print('waiting...')
      continue
    elif statusCode != 200:
      raise Exception('bad response: %s' % json.dumps(r))

    with open('t.json', 'w') as outf:
      outf.write(json.dumps(r))

    break

  for request in r['data']['runs']['1']['firstView']['steps'][0]['requests']:
    if keys['url'] == request['full_url']:
      body_url = 'https://www.webpagetest.org/response_body.php?test=%s&run=1&cached=0&bodyid=%s' % (
        r['data']['id'], request['body_id'])

      print("fetching body...")
      body = urllib.request.urlopen(body_url).read().decode('utf8')
      lsd = re.findall('name="lsd" value="([^"]*)"', body)[0]
      with open(localfname('fb_lsd.txt'), 'w') as outf:
        outf.write(lsd)
    if '__user' in request['url']:
      with open(localfname('fb_dyn_fetch.txt'), 'w') as outf:
        outf.write(json.dumps(request))

  for request in r['data']['runs']['1']['firstView']['steps'][-1]['requests']:     
    if '/comment_fetch.php' in request['url']:
      with open(localfname('fb_comment_fetch.txt'), 'w') as outf:
        outf.write(json.dumps(request))
    elif '/reply_fetch.php' in request['url']:
      with open(localfname('fb_reply_fetch.txt'), 'w') as outf:
        outf.write(json.dumps(request))
      
if __name__ == '__main__':
  start()
