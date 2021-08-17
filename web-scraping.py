from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import psycopg2

host = "localhost"
username = "postgres"
password = "password"
database = "agriculturedb"
port = "5432"

conn = psycopg2.connect(host=host, port=port, dbname=database, user=username, password=password)
cursor = conn.cursor()


def parse_data_from_website():
    url = "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=78&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01" \
          "-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead=Tomato" \
          "&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select-- "

    page_content = requests.get(url).text

    # soup object to collect the required data
    soup = BeautifulSoup(page_content, "lxml")

    # extracting the table and table data from the site
    tomato_price_table = soup.find("table", {"class": "tableagmark_new"})
    tomato_price_table_data = tomato_price_table.find_all("tr")

    # print(tomato_price_table_data)
    table_data = []
    for tr in tomato_price_table.find_all("tr")[1:]:  # ignoring the tr with style
        t_row = []
        # print("TR = ",tr.text)
        for td in tr.find_all("td"):
            # print("TD = ",td.text)
            td_text = td.text.replace('\n', ' ').strip()
            if len(td_text) != 0:
                t_row.append(td_text)
        if len(t_row) != 0:
            # print(t_row)
            table_data.append(t_row)

    return table_data


""""
    # Extracting column headings
    col_headings = []
    for th in tomato_price_table_data[0].find_all("th"):
        # remove any newlines and extra spaces from left and right
        col_headings.append(th.b.text.replace('\n', ' ').strip())

    print(col_headings)"""


def insert(data_arr, conn):
    # insert_query = "INSERT INTO test_table values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    # cursor.execute(insert_query, data_arr[0])
    # conn.commit()
    print(len(data_arr))
    for row in range(len(data_arr)):
        insert_query = "INSERT INTO test_table(districtname , marketname, commodity, variety , grade, " \
                       "minprice , maxprice , modalprice , pricedate ) values (%s, %s, %s, %s, %s, %s, " \
                       "%s, %s, %s); "
        cursor.execute(insert_query, data_arr[row][1:])
    conn.commit()


parsed_data = parse_data_from_website()
print(parsed_data)
insert(parsed_data, conn)

