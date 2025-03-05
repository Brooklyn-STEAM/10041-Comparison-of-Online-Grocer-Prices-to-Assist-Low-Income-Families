from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
# >>> re.sub('<[^>]+>', '', s)

driver = webdriver.Chrome()
driver.get("https://shop.foodbazaar.com/store/food-bazaar/s?k=eggs")
assert "Food Bazaar" in driver.title

# search = driver.find_element(By.ID, "search-bar-input")
# search.send_keys("" + Keys.RETURN)


# Filter Search
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]

time.sleep(2)


# List of Names + Prices
temp = soup.find_all('div', class_="e-147kl2c")
i = 0
names = []
for name in temp:
    s = name
    names.append(re.sub("<.+?>", "", str(s)))
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


# Aggregates Name and Prices
items = dict()

index = 0
for index in range(len(names)):
    items.update({str(names[index]):str(prices[index])})


# Writes to File
text = open("text.txt", "w")
last_key = list(items)[-1]
for item in items:
    if last_key == item:
        text.write(item + ": " + items.get(item))
    else:
        text.write(item + ": " + items.get(item) + "\n\n")
text.close()

driver.quit()