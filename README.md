# agmarkWebsiteCrawling
Completed the first four tasks under the Agmark Website Crawling assignment

Database used: Postgresql

Steps to execute:
1. Initialise and activate virtual environment
2. Install requirements
pip install -r requirements.txt
3. Run program with the following command
python web-scraping.py <arg>
  where <arg> can be:
  1. task_all : for obtaining data for all commodities in all states, districts and markets and storing the data into table <i>commoditywise_table</i>
  2. task1 : for obtaining data for all commodities in State = Maharashtra, District = Pune, Market = Pune(Khadiki) and storing the data into table <i>marketwise_table</i>
  3. task2 : for obtaining data for all commodities in State = Maharashtra, District = Pune and storing the data into table <i>districtwise_table</i>
  4. task3 : for obtaining data for all commodities in State = Maharashtra and storing the data into table <i>statewise_table</i>
  
Please note: Included a pgdump of the tables created in task1 and task2. Did not include task3 and task_all in interest of time taken to execute.
  Dump filename: agriculturedb.sql
  
Assumptions:
  1. State, district and market name and code has been hard coded as per the assignment requirement. To make it customizable, we would have to scrape through all the options just like we did for commodities and access it as a user input, which we have not.
  2. Created separate tables for separate tasks even though the table schema is the same.
  3. Dates are hardcoded from 01-Jan-2021 to 10-Aug-2021
