import time
from selenium import webdriver
from bs4 import BeautifulSoup
import psycopg2
import urllib
from selenium.webdriver.chrome.options import Options

host = "localhost"
username = "postgres"
password = "password"
database = "agriculturedb"
port = "5432"

conn = psycopg2.connect(host=host, port=port, dbname=database, user=username, password=password)
cursor = conn.cursor()


def wait_for(condition_function, last_row, driver):
    start_time = time.time()
    while time.time() < start_time + 20:
        if condition_function(last_row, driver):
            return True
        else:
            time.sleep(1)
    raise Exception('Timeout')


def page_hasLoaded(last_row, driver):
    try:
        table = driver.find_element_by_class_name('tableagmark_new')
        curr = table.find_elements_by_tag_name("tr")[50].find_element_by_tag_name("td").text
        if curr == last_row:
            return False
        else:
            return True
    except Exception:
        return False


def get_commodity_values_list(driver, comm_names):
    commodity_list = []

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
        commodity_list.append(element["value"])
        comm_names.append(urllib.quote(element.text))
    return commodity_list


def parse_data_from_website():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    DRIVER_PATH = './chromedriver'
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    commodity_names = []
    commodity_list = get_commodity_values_list(driver, commodity_names)

    # print(commodity_names[1])

    for url_for_each_comm in range(2):
        url = 'https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity='+commodity_list[url_for_each_comm]+'&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom=01-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead='+commodity_names[url_for_each_comm]+'&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--'
        # print(url)
        driver.get(url)

        for page in range(2):
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, "lxml")
            tomato_price_table = soup.find("table", {"class": "tableagmark_new"})

            # print(tomato_price_table.find_all("tr")[1].find("td").text)

            # Data extraction
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

            insert(table_data)

            table = driver.find_element_by_class_name('tableagmark_new')
            # print(table)

            last_row = table.find_elements_by_tag_name("tr")[50].find_element_by_tag_name("td").text
            # table.find_elements_by_tag_name("tr")[52].find_element_by_tag_name("input").click()
            driver.find_element_by_xpath(
                "//input[@onclick=\"javascript:__doPostBack('ctl00$cphBody$GridPriceData','Page$Next');return false;\"]").click()

            wait_for(page_hasLoaded, last_row, driver)

    driver.quit()


def insert(data_arr):
    # print(len(data_arr))
    for row in range(len(data_arr)):
        insert_query = "INSERT INTO test_table(districtname , marketname, commodity, variety , grade, " \
                       "minprice , maxprice , modalprice , pricedate ) values (%s, %s, %s, %s, %s, %s, " \
                       "%s, %s, %s); "
        cursor.execute(insert_query, data_arr[row][1:])
    conn.commit()


parse_data_from_website()
