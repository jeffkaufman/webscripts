import json
import subprocess
from seleniumwire import webdriver

HEADERS_FNAME = "fb_%s_headers.json"
BODY_FNAME = "fb_%s_request_body.urlencoded"

def save_graphql_request(n, requests):
  graphql_requests = [x for x in requests if 'graphql/' in x.path]

  r = graphql_requests[0]
  with open(HEADERS_FNAME % n, "w") as outf:
    outf.write(json.dumps(dict(r.headers)))
  with open(BODY_FNAME % n, "wb") as outf:
    outf.write(r.body)  

def run(driver):
  def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  

  driver.implicitly_wait(10)

  driver.get('https://www.facebook.com/jefftk/posts/989260955992')
  scroll_down()
  
  len_pre_click_requests = len(driver.requests)
  driver.find_element_by_css_selector(
    '[data-testid="UFI2CommentsCount/root"]').click()
  save_graphql_request(1, driver.requests[len_pre_click_requests:])
  
  scroll_down()
  len_pre_click_requests = len(driver.requests)
  driver.find_element_by_css_selector(
    '[data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]').click()
  save_graphql_request(2, driver.requests[len_pre_click_requests:])

  scroll_down()
  len_pre_click_requests = len(driver.requests)
  driver.find_element_by_css_selector(
    '[data-testid="UFI2CommentsPagerRenderer/pager_depth_1"]').click()
  save_graphql_request(3, driver.requests[len_pre_click_requests:])
  
def slurp():
  driver = webdriver.Chrome()
  try:
    run(driver)
  finally:
    #driver.close()
    pass

def copy_up():
  subprocess.run(["scp",
                  HEADERS_FNAME % 1, BODY_FNAME % 1,
                  HEADERS_FNAME % 2, BODY_FNAME % 2,
                  HEADERS_FNAME % 3, BODY_FNAME % 3,
                  "www.jefftk.com:wsgi/"])

def start():
  slurp()
  copy_up()

if __name__ == "__main__":
  start()
