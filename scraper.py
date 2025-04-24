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
search = "Turnip"
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
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]


# List of Names + Prices
temp = soup.find_all('div', class_="e-147kl2c")
i = 0
names = []
for name in temp:
    names.append(name.text)
    i += 1
    if i == 10:
        break

temp = soup.find_all('span', class_="e-1ip314g")
i = 0
prices = []
for price in temp:
    text = price.text
    char = re.sub("[^0-9]", "", text)
    float_price = int(char) / 100

    prices.append(float_price)
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
    temp = foodbazaar.get(item)
    items.append(temp)
items.sort()

for item in foodbazaar:
    if foodbazaar.get(item) == items[0]:
        name = item
        price = items[0]
        break

foodbazaar = []
foodbazaar.append(name)
foodbazaar.append(price)

conn = conn_db()
cursor = conn.cursor()

cursor.execute("SELECT `id` FROM `CompanyList` WHERE `company_name` = 'Food Bazaar';")
fb_name = cursor.fetchone()["id"]

cursor.close()
conn.close()





## Walmart
driver.get(f"https://www.walmart.com/search?q={search}")


# Filter Tags
time.sleep(2)

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
        names.append(name.text)
    i += 1
    if i == 16:
        break

temp = soup.find_all(class_="w_iUH7")
i = 0
prices = []
for price in temp:
    if "current price" in price.text:
        text = price.text
        text = re.sub("[^0-9]", "", text)
        prices.append(text)
    i += 1
    if i == 90:
        break


# Aggregates Name and Price
walmart = dict()

index = 0
for index in range(len(names)):
    walmart.update({str(names[index]):str(prices[index])})


# Calculations
items = []
for item in walmart:
    temp = walmart.get(item)
    temp = int(temp) / 100
    items.append(temp)
items.sort()

for item in walmart:
    convert = int(walmart.get(item)) / 100
    if convert == items[0]:
        name = item
        price = items[0]
        break

walmart = []
walmart.append(name)
walmart.append(price)

conn = conn_db()
cursor = conn.cursor()

cursor.execute("SELECT `id` FROM `CompanyList` WHERE `company_name` = 'Walmart';")
walmart_name = cursor.fetchone()["id"]

cursor.close()
conn.close()





## Aldi
driver.get(f"https://new.aldi.us/results?q={search}")


# Filter Tags
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta", "option", "form", "link", "head", "button"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]


# List of Names + Prices
temp = soup.find_all("div", class_="product-tile__name")
i = 0
names = []
for name in temp:
    names.append(name.text)
    i += 1
    if i == 5:
        break

temp = soup.find_all("span", class_="base-price__regular")
i = 0
prices = []
for price in temp:
    prices.append(price.text)
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
    temp = aldi.get(item)
    items.append(temp)
items.sort()

for item in aldi:
    if aldi.get(item) == items[0]:
        name = item
        price = items[0][1:]
        break

aldi = []
aldi.append(name)
aldi.append(price)

conn = conn_db()
cursor = conn.cursor()

cursor.execute("SELECT `id` FROM `CompanyList` WHERE `company_name` = 'Aldi';")
aldi_name = cursor.fetchone()["id"]

cursor.close()
conn.close()


driver.quit()





conn = conn_db()
cursor = conn.cursor()


cursor.execute(f"""
            INSERT INTO `Products`
               (`item_name`, `item_image`)
            VALUES
               ('{search}', 'temp')
            ON DUPLICATE KEY UPDATE
               `item_name` = '{search}';
""")

cursor.execute(f"SELECT `id` FROM `Products` WHERE `item_name` = '{search}';")

values = cursor.fetchone()

product_id = values.get("id")


cursor.execute("""
            INSERT INTO `Comparison`
                (`product_id`, `product_name`, `product_price`, `company`)
            VALUES
                (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `product_id` = %s,
                `product_name` = %s,
                `product_price` = %s,
                `company` = %s;
""", (str(product_id), foodbazaar[0], foodbazaar[1], fb_name, str(product_id), foodbazaar[0], foodbazaar[1], fb_name))

cursor.execute("""
            INSERT INTO `Comparison`
                (`product_id`, `product_name`, `product_price`, `company`)
            VALUES
                (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `product_id` = %s,
                `product_name` = %s,
                `product_price` = %s,
                `company` = %s;
""", (str(product_id), walmart[0], walmart[1], walmart_name, str(product_id), walmart[0], walmart[1], walmart_name))

cursor.execute("""
            INSERT INTO `Comparison`
                (`product_id`, `product_name`, `product_price`, `company`)
            VALUES
                (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `product_id` = %s,
                `product_name` = %s,
                `product_price` = %s,
                `company` = %s;
""", (str(product_id), aldi[0], aldi[1], aldi_name, str(product_id), aldi[0], aldi[1], aldi_name))


cursor.close()
conn.close()