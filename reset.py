## RESETS 'items.txt' FILE ##
## DO NOT RESET UNTIL AFTER SCRAPER FINISHES RUNNING ##

from selenium import webdriver
import pymysql
from dynaconf import Dynaconf
from fake_useragent import UserAgent
import undetected_chromedriver as uc




## Setup
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

conn = conn_db()
cursor = conn.cursor()
cursor.execute(f"""
    SELECT `item_name` FROM `Products`;
""")
searches = cursor.fetchall()
cursor.close()
conn.close()

filterSearches = []
for item in searches:
    temp = item["item_name"]
    if len(temp) < 3:
        pass
    else:
        filterSearches.append(temp)

with open("items.txt", "w") as items:
    for item in filterSearches:
        if item == filterSearches[-1]:
            items.write(item)
        else:
            items.write(item + "\n")