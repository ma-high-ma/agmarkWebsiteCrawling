from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import mysql.connector

host = "localhost"
username = "user"
password = "pass"

# mydb = mysql.connector.connect(host=host, username=username, password=password)
#
# mycursor = mydb.cursor()
#
# mycursor.execute("CREATE DATABASE mydatabase")
#
# mycursor.execute("SHOW DATABASES")
#
# for x in mycursor:
#   print(x)


url = "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=78&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01" \
      "-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead=Tomato" \
      "&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select-- "

page_content = requests.get(url).text

# soup object to collect the required data
soup = BeautifulSoup(page_content, "lxml")

# extracting the table and table data from the site
tomato_price_table = soup.find("table", {"class": "tableagmark_new"})
tomato_price_table_data = tomato_price_table.find_all("tr")
# tomato_price_table_data = tomato_price_table_data[1:]

# print(tomato_price_table_data)

# Extracting column headings
col_headings = []
for th in tomato_price_table_data[0].find_all("th"):
    # remove any newlines and extra spaces from left and right
    col_headings.append(th.b.text.replace('\n', ' ').strip())

print(col_headings)

table_data = []
for tr in tomato_price_table.find_all("tr")[1:]:  # find all tr's from table's tbody
    t_row = []
    # print("TR = ",tr.text)
    for td in tr.find_all("td"):
        # print("TD = ",td.text)
        t_row.append(td.text.replace('\n', ' ').strip())
    table_data.append(t_row)

print(table_data)

