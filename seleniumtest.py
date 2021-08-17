import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 20:
        if condition_function():
            return True
        else:
            time.sleep(1)
    raise Exception(
        'Timeout waiting for '
    )


def page_hasLoaded():
    try:
        table = driver.find_element_by_class_name('tableagmark_new')
        curr = table.find_elements_by_tag_name("tr")[50].find_element_by_tag_name("td").text
        if curr == last_row:
            return False
        else:
            return True
    except Exception:
        return False


options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

DRIVER_PATH = './chromedriver'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get('https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=78&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom'
           '=01-Jan-2021&DateTo=10-Aug-2021&Fr_Date=01-Jan-2021&To_Date=10-Aug-2021&Tx_Trend=0&Tx_CommodityHead'
           '=Tomato&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--')
# print(driver.page_source)
table = driver.find_element_by_class_name('tableagmark_new')
last_row = table.find_elements_by_tag_name("tr")[50].find_element_by_tag_name("td").text
print (last_row)
table.find_elements_by_tag_name("tr")[52].find_element_by_tag_name("input").click()

# time.sleep(10)

wait_for(page_hasLoaded)

# driver.find_element_by_xpath("//input[@onclick=\"javascript:__doPostBack('ctl00$cphBody$GridPriceData','Page$Next');return false;\"]").click()

driver.save_screenshot('ss.png')
driver.quit()
