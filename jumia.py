from gspread.models import Worksheet
import requests
from lxml import html
from urllib.parse import urljoin
from datetime import datetime
import argparse
import gspread
import time

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36", 
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})

scraped_data = []
COUNTER = 0 

def parse(content):
    global COUNTER
    for link in content.xpath("//section[@class='card -fh']/div/article"):
        product_name_obj = link.xpath(".//div[@class='info']//h3[@class='name']/text()")
        price_obj = link.xpath(".//div[@class='info']//div[@class='prc']/text()")
        discount_obj = link.xpath(".//div[@class='info']//div[@class='old']/text()")
        stars_obj = link.xpath(".//div[@class='stars _s']/text()")
        reviews_count_obj = link.xpath(".//div[@class='rev']/text()")
        
        product_name = parse_obj(product_name_obj)

        price = parse_obj(price_obj)
            
        discount = parse_obj(discount_obj)
        
        try:
            stars = stars_obj[0].split(" ")[0]
        except:
            stars = ""
        
        try:
            reviews_count = reviews_count_obj[0].strip("()")
        except:
            reviews_count = "" 
        
        if product_name:
            if COUNTER < 100:
                scraped_data.append([product_name, price, discount, stars, reviews_count])
                COUNTER += 1
            else:
                return

    next_page = link.xpath("//a[@aria-label='Next Page']/@href")
    
    if next_page:
        # trying to avoid bot detection  
        time.sleep(5)
        url = urljoin("https://www.jumia.com.ng/", next_page[0])
        request(url)

def request(url):
    page = SESSION.get(url)
    content = html.fromstring(page.content)
    parse(content)

def parse_obj(obj):
    try:
        clean_obj = obj[0]
    except:
        clean_obj = ""

    return clean_obj

def save_data(email):
    if scraped_data:
        gc = gspread.service_account(filename='creds.json')
        file_name = "Jumia Scrapped Data " + str(datetime.now())

        sh = gc.create(file_name)
        sh.share(email, perm_type='user', role='writer')

        worksheet = sh.sheet1
        worksheet.format('A1:E1', {'textFormat': {'bold': True}})
        worksheet.append_row(["Product Name", "Price", "Discounted Price", "Stars Rating", "Number Of Review"])

        range = "A2:" + str(len(scraped_data) + 1)
        worksheet.batch_update([{'range': range, 'values': scraped_data}])
        

def main():
    parser = argparse.ArgumentParser(description='Scrap Jumia Product info')
    
    # defining a parser that lets us specify a download date range
    parser.add_argument('-e', '--email', default="ibiloyes@gmail.com", type=str, 
                        help="Specify the link where the Output Spreadsheet link will be sent")
    args = parser.parse_args()    

    print("[*] Scraping Bot starting....")
    SESSION.get("https://jumia.com.ng")
    
    url = "https://www.jumia.com.ng/health-care/"

    
    request(url)

    save_data(args.email)
    
    print("[*] Scraping is Completed!!!!")
main()