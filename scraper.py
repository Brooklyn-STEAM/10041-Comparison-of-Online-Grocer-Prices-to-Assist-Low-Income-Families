from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

# Search Input
search = "cheese"

driver = webdriver.Chrome()

# Food Bazaar
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
    letter = 1
    combine = ""
    for char in re.sub("<.+?>", "", str(name)):
        if letter < 50:
            combine = combine + char
            letter += 1
        else:
            combine = combine + "..."
            break
    names.append(combine)
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
items = dict()

index = 0
for index in range(len(names)):
    items.update({str(names[index]):str(prices[index])})


# Empty File
text = open("foodbazaar.txt", "w").close()


# Writes to File
with open("foodbazaar.txt", "a") as text:
    last_key = list(items)[-1]
    for item in items:
        if last_key == item:
            text.write(item + ": " + items.get(item))
        else:
            text.write(item + ": " + items.get(item) + "\n")


#Amazon
driver.get("https://www.amazon.com/gp/")
time.sleep(0.5)
driver.get(f"https://www.amazon.com/s?k=amazon+fresh+{search}&crid=E4LH7VD545UQ&sprefix=amazon+fresh+{search}%2Caps%2C100&ref=nb_sb_noss_1")


# Filter Tags
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'lxml')

unwanted_tags = ["style", "script", "meta", "option", "form", "link", "head"]

for tag in unwanted_tags:
    [s.extract() for s in soup(tag)]

# List of Names + Prices
temp = soup.select(".a-size-base-plus.a-spacing-none.a-color-base.a-text-normal")
i = 0
names = []
for name in temp:
    if i > 2:
        letter = 1
        combine = ""
        for char in re.sub("<.+?>", "", str(name)):
            if letter < 50:
                combine = combine + char
                letter += 1
            else:
                combine = combine + "..."
                break
        names.append(combine)
    i += 1
    if i == 6:
        break

stuff = soup.find_all("span", class_="a-price")
for item in stuff:
    if "a-text-price" in item.get("class"):
        item.span.decompose()
        stuff.remove(item)

new_list = []
for item in stuff:
    word = re.sub("<.+?>", "", str(item))
    new_word = word[:len(word)//2 + len(word)%2]
    new_list.append(new_word)

for item in new_list:
    if item is None:
        new_list.pop(new_list.index(item))

i = 0
prices = []
for price in new_list:
    if i > 3:
        prices.append(price)
    i += 1
    if i == 7:
        break


# Aggregates Name and Price
items = dict()

index = 0
for index in range(len(names)):
    items.update({str(names[index]):str(prices[index])})


# Empty File
text = open("amazon.txt", "w").close()


# Writes to File
with open("amazon.txt", "a") as text:
    last_key = list(items)[-1]
    for item in items:
        if last_key == item:
            text.write(item + ": " + items.get(item))
        else:
            text.write(item + ": " + items.get(item) + "\n")

# driver.quit()

input()