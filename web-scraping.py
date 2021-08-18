import time
from selenium import webdriver
from bs4 import BeautifulSoup
import psycopg2
import urllib

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import sys


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
        curr = table.find_elements_by_tag_name("tr")[-3].find_element_by_tag_name("td").text
        # curr = driver.find_element_by_xpath("(//table/tbody/tr)[last()]")
        print('curr = ', curr)
        if curr == last_row:
            return False
        else:
            return True
    except Exception:
        return False


def data_extraction(page):
    soup = BeautifulSoup(page, "lxml")
    tomato_price_table = soup.find("table", {"class": "tableagmark_new"})

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
            print(t_row[0])
            table_data.append(t_row)
    return table_data


def data_read_and_insert(driver, conn, tablename):
    while True:
        page_content = driver.page_source
        table_values = data_extraction(page_content)
        print('length of table values = ', len(table_values))
        if len(table_values) == 1:
            break
        insert_into_db(table_values, conn, tablename)

        table = driver.find_element_by_class_name('tableagmark_new')
        # print(table)

        last_row = table.find_elements_by_tag_name("tr")[-3].find_element_by_tag_name("td").text
        # last_row = driver.find_element_by_xpath("(//table/tbody/tr)[last()]")
        print('last row = ', last_row)

        try:
            # table.find_elements_by_tag_name("tr")[52].find_element_by_tag_name("input").click()
            driver.find_element_by_xpath(
                "//input[@onclick=\"javascript:__doPostBack('ctl00$cphBody$GridPriceData','Page$Next');return false;\"]").click()

        except NoSuchElementException:
            return
        wait_for(page_hasLoaded, last_row, driver)


def parse_all_data_from_website(driver, conn, task):
    commodity_names = []
    commodity_list = get_commodity_values_list(driver, commodity_names)

    code_state, code_district, code_market = '0', '0', '0'
    name_state, name_district, name_market = "--Select--", "--Select--", "--Select--"

    if task == "task1":
        name_table = "commoditywise_table"
    if task == "task2":
        name_table = "marketwise_table"
        code_state = "MH"
        name_state = "Maharashtra"
        code_district = "14"
        name_district = "Pune"
        code_market = "2495"
        name_market = "Pune(Khadiki)"
    elif task == "task3":
        name_table = "districtwise_table"
        code_state = "MH"
        name_state = "Maharashtra"
        code_district = "14"
        name_district = "Pune"
    elif task == "task4":
        name_table = "statewise_table"
        code_state = "MH"
        name_state = "Maharashtra"

    for url_for_each_comm in range(2):
        print(commodity_names[url_for_each_comm])
        driver = url_manipulation(driver, commodity_list[url_for_each_comm], commodity_names[url_for_each_comm],
                                  code_state, name_state, code_district, name_district, code_market, name_market)
        data_read_and_insert(driver, conn, name_table)
    driver.quit()


def insert_into_db(data_arr, conn, table_name):
    cursor = conn.cursor()
    # print(len(data_arr))
    for row in range(len(data_arr)):
        insert_query = "INSERT INTO "+table_name+"(districtname , marketname, commodity, variety , grade, " \
                       "minprice , maxprice , modalprice , pricedate , lastmodified ) values (%s, %s, %s, %s, %s, %s, " \
                       "%s, %s, %s, CURRENT_TIMESTAMP); "
        cursor.execute(insert_query, data_arr[row][1:])
    conn.commit()


def url_manipulation(driver, commodity_code, commodity_name, state_code, state_name, district_code, district_name,
                     market_code,
                     market_name):
    url = 'https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=' + commodity_code + '&Tx_State=' + state_code + '&Tx_District=' + district_code + '&Tx_Market=' + market_code + '&DateFrom=01-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead=' + commodity_name + '&Tx_StateHead=' + state_name + '&Tx_DistrictHead=' + district_name + '&Tx_MarketHead=' + market_name
    driver.get(url)
    return driver


def main():
    host = "localhost"
    username = "postgres"
    password = "password"
    database = "agriculturedb"
    port = "5432"

    conn = psycopg2.connect(host=host, port=port, dbname=database, user=username, password=password)
    print('database connection secured')

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    DRIVER_PATH = './chromedriver'
    try:
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    except:
        print('driver issue')

    print('driver set up complete')

    tasks = ["task1", "task2", "task3", "task4"]
    choice = sys.argv[1]
    if choice in tasks:
        parse_all_data_from_website(driver, conn, sys.argv[1])
    else:
        print('Refer to README to run the code')



if __name__ == '__main__':
    main()
