from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import time
import argparse
import os
import gspread


def parse(browser, email):
    scraped_data = []
    
    gc = gspread.service_account(filename='creds.json')
    file_name = "Jumia Food Scrapped Data " + str(datetime.now())

    sh = gc.create(file_name)
    sh.share(email, perm_type='user', role='writer')

    worksheet = sh.sheet1
    worksheet.format('A1:G1', {'textFormat': {'bold': True}})
    worksheet.append_row(["Category", "ItemName", "Description", "Price", "Option Name", "Option", "Option Price"])
        
    for category in browser.find_elements_by_xpath("//section[@class='menu-category-section mtxxl']"):
        category_name = category.find_element_by_xpath(".//div[@class='vendor-category-info mbs']/p").text
        for product in category.find_elements_by_xpath(".//article[@class='product-card']"):
            try:
                itemName = product.find_element_by_xpath(".//h3[@class='product-title']/span").text
            except:
                continue
            description = product.find_element_by_xpath(".//p").text
            price = product.find_element_by_xpath(".//a/span").text

            see_more = category.find_element_by_xpath(".//i[@class='fa fa-plus-square-o']").click()
            
            for option in browser.find_elements_by_xpath("//div[@class='mtl']//div[@class='mtm']"):
                optionName = browser.find_element_by_xpath("//div[@class='mtl']//div[@class='mtm']/p").text
                for opt in option.find_elements_by_xpath(".//div[@class='dir-row is-size-5']"):
                    option_text = opt.find_element_by_xpath(".//label").text
                    try:
                        option_price = opt.find_element_by_xpath(".//div[@class='dif pls fsh-0 mla']").text
                    except:
                        option_price = ""      
                    scraped_data.append([category_name, itemName, description, price, optionName, option_text, option_price]) 
            try:
                browser.find_element_by_xpath("//button[@class='close-popup mla']/i[@class='delete']").click()
            except:
                continue
        
        time.sleep(2)


    if scraped_data:
        range = "A2:" + str(len(scraped_data) + 1)
        worksheet.batch_update([{'range': range, 'values': scraped_data}])


def main():
    parser = argparse.ArgumentParser(description='Scrap Jumia Food Product info')
    
    # defining a parser that lets us specify a download date range
    parser.add_argument('-u', '--url', default="https://food.jumia.com.ng/restaurant/n4gn/chicken-republic-mobil-ogba", type=str,
                        help="""Provide a Jumia Food location url to get data from""")
    parser.add_argument('-e', '--email', default="ibiloyes@gmail.com", type=str, 
                        help="Specify the link where the Output Spreadsheet link will be sent")
    args = parser.parse_args()
    
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    print(args.email)
    print(args.url)
    
    browser = webdriver.Chrome(executable_path="./chromedriver")

    # browser = webdriver.Firefox(executable_path="./geckodriver")
    
    print("[*] STARTING Scraper.....")  
    
    browser.get(args.url)
    
    time.sleep(5)
    
    input_field = browser.find_element_by_xpath("//input[@placeholder='Enter your delivery address']")
    input_field.send_keys("Ogba Bus Stop")
    
    time.sleep(5)
    
    button = browser.find_element_by_xpath("//div[@class='geo-option'][1]")
    button.click()
    
    time.sleep(5)
    
    browser.find_element_by_xpath("//button[@class='button mvs fw is-success']").click()
    
    time.sleep(5)
    
    parse(browser, args.email)
        
    print("[*] Scraping is Completed.....")
    browser.close()          
    browser.quit()
main()