# == Modules == #
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from requests import Session
from bs4 import BeautifulSoup

from pyautogui import click

from time import sleep
# =================================================================================================== #
FIFA_SITE = 'https://www.ea.com/fifa/ultimate-team/web-app/'

SEARCH_URL = "https://www.futwiz.com/en/searches/player22/"
PLAYER_URL = "https://www.futwiz.com/en/fifa22/player/"

USER_DATA_DIR = r'C:\Users\LEGION\AppData\Local\Google\Chrome\User Data\Default'
USER_AGENT = 'selenium'

X = 1760
Y = 350
# =================================================================================================== #

# --- Functions -- #
    
def get_player_price(player_data):
    session = Session()
    
    URL = SEARCH_URL + player_data["name"]

    versions = session.get(URL).json()

    if versions:
        for version in versions:
            if (version["rating"] == player_data["rating"] and version["position"] == player_data["position"]):
                player_url = f"{version['urlname']}/{version['lineid']}"
                player_page = BeautifulSoup(session.get(PLAYER_URL + player_url).content, "html.parser")

                price = int(player_page.find_all("div", class_="playerprofile-price text-center")[2].text.strip().replace(",", ""))

                return price, int(version["pcminprice"]), int(version["pcmaxprice"])
    
    return [None]*3

def sell_price(price, MIN, MAX):
    
    if (price is None):
        return [None]*2

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

def sell(browser, start, buy_now):
    browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[1]/button').click()
    
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

# -- login -- #
while True:
    login = browser.find_element(By.XPATH, '//*[@id="Login"]/div/div/button[1]')
    if (login.is_enabled()):
        login.click()
        break
    sleep(0.25)

# -- get to players -- #
transfers = browser.find_element(By.XPATH, '/html/body/main/section/nav/button[3]')
transfers.click()
sleep(1)

transfers_list = browser.find_element(By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]')
transfers_list.click()
sleep(1)


# -- Select Players -- #
browser.implicitly_wait(0.5)
# players list
available_number = len(browser.find_elements(By.CLASS_NAME, 'itemList')[2].find_elements(By.CLASS_NAME, 'listFUTItem'))
# unsold players
unsold_number = len(browser.find_elements(By.CLASS_NAME, 'itemList')[1].find_elements(By.CLASS_NAME, 'listFUTItem'))
browser.implicitly_wait(15)

# -- sell players -- #
players_number = available_number + unsold_number
skip = 0
for p in range(players_number):

    # select player
    if (p < available_number):
        players_list = browser.find_elements(By.CLASS_NAME, 'itemList')[2].find_elements(By.CLASS_NAME, 'listFUTItem')
    else:
        players_list = browser.find_elements(By.CLASS_NAME, 'itemList')[1].find_elements(By.CLASS_NAME, 'listFUTItem')
    player = players_list[skip]
    try:
        player.click()
    except:
        continue

    # get player data
    name = player.find_element(By.CLASS_NAME, 'name').text
    rating = player.find_element(By.CLASS_NAME, 'rating').text
    position = player.find_element(By.CLASS_NAME, 'position').text
    player_data = {'name': name, 'position': position, 'rating': rating}

    # get player price
    price, min_price, max_price = get_player_price(player_data)

    # get bid & buy now price
    start, buy_now = sell_price(price, min_price, max_price)

    # skip if player price wasn't found
    if (start is None):
        skip += 1
        continue

    # sell player
    sell(browser, start, buy_now)
    sleep(1)


# ====================================================================================================================== #