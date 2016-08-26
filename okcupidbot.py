import sys, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# helper method for selenium
def element_id_exists(driver, id):
    try:
        driver.find_element_by_id(id)
        return True
    except NoSuchElementException:
        return False

# takes a webdriver, username, and password and logs into OkCupid
def login(driver, username, password):
    driver.get('https://www.okcupid.com/login')
    elem = driver.find_element_by_id('login_username')
    elem.send_keys(username)
    elem = driver.find_element_by_id('login_password')
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

    driver.get('https://www.okcupid.com/')
    assert "Welcome!" in driver.title, "Login failed!"

# takes a webdriver. navigates to the browse matches page and extracts urls for all matches
def extractMatches(driver):
    rarr = []
    driver.get('https://www.okcupid.com/match')

    while not element_id_exists(driver, 'match_bs'):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

    matches = driver.find_elements_by_xpath("//div[@class='match_card']/a[@class='image_link']")

    for match in matches:
        url = match.get_attribute('href')
        rarr.append(url)

    return rarr

# takes a webdriver, list of urls, file of past usernames viewed (split by newlines), and timeout.
# visits each url with timeout milliseconds between each request if the user hasn't already been visited
def visitMatches(driver, matchurls, f, timeout):
    atleastonevisit = False
    f.seek(0)
    prevvisits = f.read().splitlines()
    f.seek(0,2)

    for url in matchurls:
        uname = url[32:url.find('?')]

        if uname not in prevvisits:
            print "Visiting user " + uname
            driver.get(url)

            prevvisits.append(uname)
            f.write(uname + '\n')

            atleastonevisit = True
            time.sleep(timeout/1000.0)
        else:
            print "User " + uname + " has already been visited!"

    assert atleastonevisit, "list of unique users has been exhausted!"

def main():
    print "Starting OkCupidBot..."

    username = sys.argv[1]
    password = sys.argv[2]
    browser = webdriver.Firefox()
    historyfile = open('visithistory.log', 'a+')

    try:
        # login
        print "Logging into OkCupid..."
        login(browser, username, password)

        while True:
            # get match URL's
            print "Extracting the latest matches..."
            matchurls = extractMatches(browser)

            # visit each match
            visitMatches(browser, matchurls, historyfile, 5000)

    except (AssertionError, KeyboardInterrupt) as e:
        print e

    print "Shutting down OkCupidBot..."
    historyfile.close()

    try:
        browser.close()
    except:
        pass    # webdriver likes to complain when it's killed by ctrl-c

    print "Done!"

main()
