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


def page_hasLoaded(first_row, driver):
    try:
        table = driver.find_element_by_class_name('tableagmark_new')
        curr = table.find_elements_by_tag_name("tr")[1].find_element_by_tag_name("td").text

        # check if last index of last page is same as last index of newly loaded page to confirm loading of new page
        if curr == first_row:
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
    # ignoring the tr with style attribute
    for tr in tomato_price_table.find_all("tr")[1:]:
        t_row = []
        for td in tr.find_all("td"):
            td_text = td.text.replace('\n', ' ').strip()
            if len(td_text) != 0:
                t_row.append(td_text)
        # expected no. of columns is 10 from the website
        if len(t_row) == 10:
            table_data.append(t_row)
    return table_data


def data_read_and_insert(driver, conn, tablename):

    # running an infinite loop till current page does not have a next button
    while True:
        page_content = driver.page_source

        # extracting data from website table and storing it in a 2D list
        table_values = data_extraction(page_content)

        # If no table data is in the page, then break from loop
        if len(table_values) == 0:
            return

        # Inserting table_values into the appropriate table
        insert_into_db(table_values, conn, tablename)

        table = driver.find_element_by_class_name('tableagmark_new')

        # Storing last index of table row in the current page
        row_first = table.find_elements_by_tag_name("tr")[1].find_element_by_tag_name("td").text

        # simulating click action on the next page button
        try:
            # table.find_elements_by_tag_name("tr")[52].find_element_by_tag_name("input").click()
            driver.find_element_by_xpath(
                "//input[@onclick=\"javascript:__doPostBack('ctl00$cphBody$GridPriceData','Page$Next');return false;\"]").click()

        except NoSuchElementException:
            return

        # wait till the next page has been loaded
        wait_for(page_hasLoaded, row_first, driver)


# retrieving data from website based on args passed
def parse_all_data_from_website(driver, conn, task):
    # storing the list of codes and names of all commodities
    commodity_names = []
    commodity_list = get_commodity_values_list(driver, commodity_names)

    # default values for each in the url when state, district and market is not selected
    code_state, code_district, code_market = '0', '0', '0'
    name_state, name_district, name_market = "--Select--", "--Select--", "--Select--"

    if task == "task_all":
        name_table = "commoditywise_table"
    if task == "task1":
        name_table = "marketwise_table"
        code_state = "MH"
        name_state = "Maharashtra"
        code_district = "14"
        name_district = "Pune"
        code_market = "2495"
        name_market = "Pune(Khadiki)"
    elif task == "task2":
        name_table = "districtwise_table"
        code_state = "MH"
        name_state = "Maharashtra"
        code_district = "14"
        name_district = "Pune"
    elif task == "task3":
        name_table = "statewise_table"
        code_state = "MH"
        name_state = "Maharashtra"

    # only top 2 commodities are being used for testing purpose and time benefit
    for url_for_each_comm in range(len(commodity_list)):

        # driver stores the page obtained from the required URL
        driver = url_manipulation(driver, commodity_list[url_for_each_comm], commodity_names[url_for_each_comm],
                                  code_state, name_state, code_district, name_district, code_market, name_market)

        # read the data from table and insert it into db
        data_read_and_insert(driver, conn, name_table)


def insert_into_db(data_arr, conn, table_name):
    cursor = conn.cursor()
    for row in range(len(data_arr)):
        insert_query = "INSERT INTO " + table_name + "(districtname , marketname, commodity, variety , grade, " \
                                                     "minprice , maxprice , modalprice , pricedate , lastmodified ) values (%s, %s, %s, %s, %s, %s, " \
                                                     "%s, %s, %s, CURRENT_TIMESTAMP); "
        cursor.execute(insert_query, data_arr[row][1:])
    conn.commit()


def url_manipulation(driver, commodity_code, commodity_name, state_code, state_name, district_code, district_name,
                     market_code, market_name):
    url = 'https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=' + commodity_code + '&Tx_State=' + state_code + '&Tx_District=' + district_code + '&Tx_Market=' + market_code + '&DateFrom=01-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead=' + commodity_name + '&Tx_StateHead=' + state_name + '&Tx_DistrictHead=' + district_name + '&Tx_MarketHead=' + market_name
    driver.get(url)
    return driver


def main():

    if len(sys.argv) != 2:
        print('Program needs 1 args. PLease refer to README.')
        return
    tasks = ["task_all", "task1", "task2", "task3"]
    # extracting args from command line input

    choice = sys.argv[1]
    if choice not in tasks:
        print('Invalid task. Refer to README to run the code')

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
        conn.close()
        return

    print('driver set up complete')
    try:
        parse_all_data_from_website(driver, conn, choice)
    except Exception as e:
        print('Error occured '+e.message)
    conn.close()
    driver.quit()


if __name__ == '__main__':
    main()
