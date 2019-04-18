import json
import subprocess
from seleniumwire import webdriver

HEADERS_FNAME = "fb_headers.json"
BODY_FNAME = "fb_request_body.urlencoded"

def run(driver):
  def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  

  driver.implicitly_wait(10)

  driver.get('https://www.facebook.com/jefftk/posts/989260955992')
  scroll_down()
  
  driver.find_element_by_css_selector(
    '[data-testid="UFI2CommentsCount/root"]').click()
  scroll_down()

  len_pre_click_requests = len(driver.requests)
  driver.find_element_by_css_selector(
    '[data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]').click()

  graphql_requests = [
    x for x in driver.requests[len_pre_click_requests:]
    if 'graphql/' in x.path]

  r = graphql_requests[0]
  with open(HEADERS_FNAME, "w") as outf:
    outf.write(json.dumps(dict(r.headers)))
  with open(BODY_FNAME, "wb") as outf:
    outf.write(r.body)
  
def slurp():
  driver = webdriver.Chrome()
  try:
    run(driver)
  finally:
    #driver.close()
    pass

def copy_up():
  subprocess.run(["scp", HEADERS_FNAME, BODY_FNAME, "www.jefftk.com:wsgi/"])

def start():
  slurp()
  copy_up()

if __name__ == "__main__":
  start()
