from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

commodity_value_list = []
commodity_list = []

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

DRIVER_PATH = './chromedriver'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(
    'https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=78&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom'
    '=01-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead'
    '=Tomato&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--')

page_content = driver.page_source
soup = BeautifulSoup(page_content, "lxml")
comm_select_list = soup.find("select", {"id": "ddlCommodity"})

option_html = [x for x in comm_select_list.find_all("option")]

# 1st value is Select i.e., no commodity selected
for element in option_html[1:]:
    commodity_value_list.append(element["value"])
    commodity_list.append(element.text)
