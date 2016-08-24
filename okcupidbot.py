import sys, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# takes a driver, username, and password and logs into OkCupid. returns a python requests session object if successful
def login(driver, username, password):
    driver.get('https://www.okcupid.com/login')
    elem = driver.find_element_by_id('login_username')
    elem.send_keys(username)
    elem = driver.find_element_by_id('login_password')
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

    driver.get('https://www.okcupid.com/')
    assert "Welcome!" in driver.title

# takes a driver. navigates to the browse matches page and extracts urls for all matches
def extractMatches(driver):
    rarr = []
    driver.get('https://www.okcupid.com/match')
    matches = driver.find_elements_by_xpath("//div[@class='match_card']/a[@class='image_link']")

    for match in matches:
        url = match.get_attribute('href')
        rarr.append(url)

    return rarr

# takes a driver, list of urls, and timeout. gets each url with timeout milliseconds between each request
def visitMatches(driver, matchurls, timeout):
    for url in matchurls:
        driver.get(url)
        time.sleep(timeout/1000.0)

def main():
    username = sys.argv[1]
    password = sys.argv[2]
    browser = webdriver.Firefox()

    # login
    print "Logging into OkCupid..."
    try:
        login(browser, username, password)
    except AssertionError:
        print "Login failed!"

    # get match URL's
    print "Extracting the latest matches..."
    matchurls = extractMatches(browser)

    # visit each match
    visitMatches(browser, matchurls, 5000)

main()
