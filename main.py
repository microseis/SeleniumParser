import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import pickle
import json
import pandas as pd

from config import website, category, npages


class Browser:
    directory = []
    savepath = []

    def get_driver(self):

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        self.driver.set_window_position(-10000, 0)
        print(self.driver.execute_script("return navigator.userAgent;"))

    def getdata(self, page, category, website_url):

        self.directory = os.getcwd() + "\\data\\"+category+"\\"

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.get_driver()
        try:
            self.driver.get(url=website_url+str(category)+'?page=' + str(page))
            time.sleep(2)
            pickle.dump(self.driver.get_cookies(), open('session', 'wb'))

            file = open(os.path.join(self.directory, "page_" + str(page) + ".html"), 'w', encoding="utf-8")
            file.write(self.driver.page_source)
            file.close()

        except Exception as ex:
            print(ex)

    def driver_close(self):
        self.driver.close()
        self.driver.quit()


def Soup(category, pages):
    titles = []
    ids = []
    barcodes = []
    brands = []
    manufacturers = []
    offer_prices = []
    base_prices = []
    discounts = []
    for page in range(0, int(pages)):
        with open(os.getcwd() + "\\data\\"+category+"\\page_"+str(page)+".html", 'r', encoding="utf-8") as file:
            src = file.read()
            soup = BeautifulSoup(src, 'lxml')
            products = soup.find('script', attrs={'id': '__NEXT_DATA__'})
            for item in products:
                python_obj = json.loads(item)
                # print(json.dumps(python_obj, indent=4, ensure_ascii=False))
                products = python_obj['props']['initialReduxState']['productsList']['products']
                for product in products:
                    title = product['title']  # название
                    id = product['id']  # код товара
                    barcode = product['barcode']['value']  # штрих-код товара
                    try:
                        brand = product['brand']['name']  # название бренда
                    except Exception as e:
                        print(e)
                        brand = ""  # название бренда
                        pass
                    try:
                        manufacturer = product['manufacturer']['name']  # производитель
                    except Exception as e:
                        print(e)
                        manufacturer = ""  # название бренда
                        pass
                    offer_price = product['offer_price'] # цена со скидкой
                    base_price = product['base_price'] # цена без скидки
                    discount = round((1-int(offer_price)/int(base_price))*100, 0) # дисконт

                    titles.append(title)
                    ids.append(id)
                    brands.append(brand)
                    barcodes.append(barcode)
                    manufacturers.append(manufacturer)
                    offer_prices.append(offer_price)
                    base_prices.append(base_price)
                    discounts.append(discount)
    df = pd.DataFrame({'ID': ids,
                       'Title': titles,
                       'Brand': brands,
                       'Barcode': barcodes,
                       'Manufacturer': manufacturers,
                       'Offer_price': offer_prices,
                       'Base_price': base_prices,
                       'Discount': discounts})
    df.to_csv("data\\"+category+"\\"+category+".csv", index=False, encoding='utf-8-sig')


if __name__ == '__main__':

    cat = category
    numofpages = npages

    browser = Browser()
    for i in range(0, int(numofpages)):
        browser.getdata("data", page=i, category=cat, website_url=website)
    browser.driver_close()

    Soup(category=cat, pages=numofpages)
