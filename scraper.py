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
search = "eggs"
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


# Empty File
text = open("foodbazaar.txt", "w").close()


# Writes to File
with open("foodbazaar.txt", "a") as text:
    for item in foodbazaar:
        if item == list(foodbazaar)[-1]:
            text.write(item + ": " + foodbazaar.get(item))
        else:
            text.write(item + ": " + foodbazaar.get(item) + "\n")





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


# Empty File
text = open("walmart.txt", "w").close()


# Writes to File
with open("walmart.txt", "a") as text:
    for item in walmart:
        if item == list(walmart)[-1]:
            text.write(item + ": " + walmart.get(item))
        else:
            text.write(item + ": " + walmart.get(item) + "\n")

# driver.quit()

conn = conn_db()

cursor = conn.cursor()

pass

cursor.close()

conn.close()

input()