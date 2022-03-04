# == Modules == #
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pyautogui import click, hotkey

from time import sleep
# =================================================================================================== #
FIFA_SITE = 'https://www.ea.com/fifa/ultimate-team/web-app/'
PRICE_SITE = 'https://www.futwiz.com/en/fifa22/player/lionel-messi/69'

USER_DATA_DIR = 'C:\Users\Mohamed\AppData\Local\Google\Chrome\User Data\Default'
USER_AGENT = 'selenium'

X = 1760
Y = 350
# =================================================================================================== #

# --- Functions -- #
def switch_to_page(browser, page):
    browser.switch_to.window(browser.window_handles[page])
    
# ---------------------------------------------------------------------------------------------- #

def get_site_price(browser, player_data):
    switch_to_page(browser, 1)

    search_bar = browser.find_element(By.XPATH, '//*[@id="globalsearch"]')
    search_bar.send_keys(player_data['name'])
    search_bar.send_keys(Keys.ARROW_DOWN)

    players = browser.find_element(By.XPATH, '//*[@id="ui-id-1"]').find_elements(By.TAG_NAME, 'li')

    if (len(players) == 0):
        search_bar.send_keys(Keys.CONTROL, 'a')
        search_bar.send_keys(Keys.DELETE)
        switch_to_page(browser, 0)
        return -1

    found = False
    for player in players:
        position = player.find_element(By.CLASS_NAME, 'drop-position').text
        rating = player.find_element(By.CLASS_NAME, 'drop-rating').text

        if ((rating == player_data['rating']) and (position == player_data['position'])):
            player.click()
            found = True
            sleep(1.5)
            break
    
    # see if player found or not
    if not found:
        search_bar.send_keys(Keys.CONTROL, 'a')
        search_bar.send_keys(Keys.DELETE)
        switch_to_page(browser, 0)
        return -1 

    
    price = browser.find_element(By.XPATH, '//*[@id="panel"]/div[4]/div/div[2]/div/div[2]/div[1]/div[3]/div[1]/div[2]').text
    price = int(price.replace(',', ''))

    switch_to_page(browser, 0)

    return price

# ---------------------------------------------------------------------------------------------- #

def sell_price(price, MIN, MAX):
    
    if (price == -1):
        return (-1, -1)

    if (price == 0):
        start = MIN
        end = MAX
    elif (price <= 1000) and (price > 0):
        start = price - 100
        end = price - 50
    elif (price <= 10000) and (price > 1000):
        start = price - 200
        end = price - 100
    elif (price > 10000):
        start = price - 2000
        end = price - 1000
    

    start = MIN if start < MIN else start
    end = MAX if end > MAX else end
    
    return start, end

# ---------------------------------------------------------------------------------------------- #

def sell(browser, start, buy_now):
    start_price = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input')
    buy_now_price = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input')
    list_for_tf = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/button')

    buy_now_price.send_keys(Keys.CONTROL, 'a')
    buy_now_price.send_keys(Keys.DELETE)
    buy_now_price.send_keys(buy_now)
    start_price.send_keys(Keys.CONTROL, 'a')
    start_price.send_keys(Keys.DELETE)
    start_price.send_keys(start)

    list_for_tf.click()

# =================================================================================================== #
          
# -- init browser -- #
service = Service(ChromeDriverManager().install())
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument(f'--user-data-dir={USER_DATA_DIR}')
options.add_argument(f'user-agent={USER_AGENT}')
options.add_argument('--disable-notifications')

browser = Chrome(service=service, options=options)
browser.implicitly_wait(15)
browser.maximize_window()

# -- init step -- #
browser.get(FIFA_SITE)
click(X, Y)
hotkey('ctrl', 't')
switch_to_page(browser, 1)
browser.get(PRICE_SITE)
switch_to_page(browser, 0)

# -- login -- #
click_shield = browser.find_element(By.XPATH, '/html/body/div[4]').get_attribute('class').split()[-1]
if (click_shield != 'showing'):
    login = browser.find_element(By.XPATH, '//*[@id="Login"]/div/div/button[1]')
    login.click()
    sleep(1)

# -- get to players -- #
transfers = browser.find_element(By.XPATH, '/html/body/main/section/nav/button[3]')
transfers.click()
sleep(1)

transfers_list = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]')
transfers_list.click()
sleep(1)

# -- players list -- #
players_list = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[3]/ul').find_elements(By.CLASS_NAME, 'listFUTItem')
players_number = len(players_list)

# -- sell players -- #
skip = 0
for _ in range(players_number):

    # select player
    players_list = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[3]/ul').find_elements(By.CLASS_NAME, 'listFUTItem')
    player = players_list[skip]
    player.click()

    # get player data
    name = player.find_element(By.CLASS_NAME, 'name').text
    rating = player.find_element(By.CLASS_NAME, 'rating').text
    position = player.find_element(By.CLASS_NAME, 'position').text
    player_data = {'name': name, 'position': f"({position})", 'rating': rating}
    sleep(0.5)

    # get player price
    price = get_site_price(browser, player_data)
    sleep(0.5)

    # get MIN & MAX price
    browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[1]/button').click()
    min_price = int(browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[2]/div[1]/span[2]').text.split()[-1].replace(',', ''))
    max_price = int(browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[3]/div[1]/span[2]').text.split()[-1].replace(',', ''))
    
    # get bid & buy now price
    start, buy_now = sell_price(price, min_price, max_price)

    # skip if player price wasn't found
    if (start == buy_now == -1):
        skip += 1
        continue

    # sell player
    sell(browser, start, buy_now)
    sleep(2)


# ====================================================================================================================== #