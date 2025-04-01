from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pymysql
from dynaconf import Dynaconf
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re




## Setup
ua = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua.random}")
driver = uc.Chrome(options=options)
search = "Eggs"
conf = Dynaconf(
    settings_file = ["settings.toml"]
)
def conn_db():
    conn = pymysql.connect(
        host = "db.steamcenter.tech",
        database = "cheap_carts",
        user = conf.username,
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )

    return conn




## Food Bazaar
driver.get(f"https://shop.foodbazaar.com/store/food-bazaar/s?k={search}")
assert "Food Bazaar" in driver.title


# Filter Search
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]


# List of Names + Prices
temp = soup.find_all('div', class_="e-147kl2c")
i = 0
names = []
for name in temp:
    names.append(re.sub("<.+?>", "", str(name)))
    i += 1
    if i == 10:
        break

temp = soup.find_all('span', class_="e-1ip314g")
i = 0
prices = []
for price in temp:
    s = price
    thing = re.sub("<.+?>", "", str(s))
    thing = thing[:-2] + "." + thing[-2:]
    prices.append(thing)
    i += 1
    if i == 10:
        break


# Aggregates Name and Price
foodbazaar = dict()

index = 0
for index in range(len(names)):
    foodbazaar.update({str(names[index]):str(prices[index])})


# Calculations
items = []
for item in foodbazaar:
    temp = float(foodbazaar.get(item)[1:]) * 100
    items.append(temp)
items.sort()

choice = "$" + str(items[0]/100)
for item in foodbazaar:
    if foodbazaar.get(item) == choice:
        name = str(item)
        price = str(choice)
        break

foodbazaar = []
foodbazaar.append(name)
foodbazaar.append(price)





## Walmart
driver.get(f"https://www.walmart.com/search?q={search}")


# Filter Tags
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta", "option", "form", "link", "head"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]


# List of Names + Prices
temp = soup.find_all("span", class_="w_V_DM")
i = 0
names = []
for name in temp:
    if i > 5:
        names.append(re.sub("<.+?>", "", str(name)))
    i += 1
    if i == 16:
        break

temp = soup.find_all(class_="w_iUH7")
i = 0
prices = []
for price in temp:
    if "current price" in re.sub("<.+?>", "", str(price)):
        price = re.sub("<.+?>", "", str(price))
        price = price.replace("current price ", "")
        prices.append(price)
    i += 1
    if i == 24:
        break


# Aggregates Name and Price
walmart = dict()

index = 0
for index in range(len(names)):
    walmart.update({str(names[index]):str(prices[index])})


# Calculations
items = []
for item in walmart:
    temp = float(walmart.get(item)[1:]) * 100
    items.append(temp)
items.sort()

choice = "$" + str(items[0]/100)
for item in walmart:
    if walmart.get(item) == choice:
        name = str(item)
        price = str(choice)
        break

walmart = []
walmart.append(name)
walmart.append(price)





## Aldi
driver.get(f"https://new.aldi.us/results?q={search}")


# Filter Tags
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta", "option", "form", "link", "head", "button"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]


# List of Names + Prices
temp = soup.find_all("div", class_="product-tile__name")
i = 0
names = []
for name in temp:
    names.append(re.sub("<.+?>", "", str(name)))
    i += 1
    if i == 5:
        break

temp = soup.find_all("span", class_="base-price__regular")
i = 0
prices = []
for price in temp:
    prices.append(re.sub("<.+?>", "", str(price)))
    i += 1
    if i == 5:
        break


# # Aggregates Name and Price
aldi = dict()

index = 0
for index in range(len(names)):
    aldi.update({str(names[index]):str(prices[index])})


# Calculations
items = []
for item in aldi:
    temp = float(aldi.get(item)[1:]) * 100
    items.append(temp)
items.sort()

choice = "$" + str(items[0]/100)
for item in aldi:
    if aldi.get(item) == choice:
        name = str(item)
        price = str(choice)
        break

aldi = []
aldi.append(name)
aldi.append(price)


# driver.quit()

conn = conn_db()
cursor = conn.cursor()

cursor.execute(f"""
            INSERT INTO `Products`
               (`item_name`, `item_image`)
            VALUES
               ('{search}', 'temp')
            ON DUPLICATE KEY UPDATE
               `item_name` = '{search}'
""")

cursor.close()
conn.close()

input()