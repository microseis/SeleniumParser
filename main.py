import json
import os
import pickle
import time
import logging

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import category, npages, website

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


logging.basicConfig(
    filename=BASE_DIR + "data/app.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)


class Browser:

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=self.options
        )

    directory = []
    savepath = []

    def get_driver(self) -> None:
        """Задание настроек для Chrome Webdriver."""
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36"
            },
        )
        self.driver.set_window_position(-10000, 0)
        self.driver.execute_script("return navigator.userAgent;")

    def get_data(self, page: int, category: int, website_url: str):
        """Метод получения данных для выбранной категории и страницы."""
        self.directory = os.getcwd() + "\\data\\" + str(category) + "\\"

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.get_driver()
        try:
            self.driver.get(url=website_url + str(category) + "?page=" + str(page))
            time.sleep(2)
            pickle.dump(self.driver.get_cookies(), open("session", "wb"))

            file = open(
                os.path.join(self.directory, "page_" + str(page) + ".html"),
                "w",
                encoding="utf-8",
            )
            file.write(self.driver.page_source)
            file.close()

        except Exception as ex:
            logging.info(ex)

    def driver_close(self) -> None:
        self.driver.close()
        self.driver.quit()


def Soup(category: int, pages: int) -> None:
    titles = []
    ids = []
    barcodes = []
    brands = []
    manufacturers = []
    offer_prices = []
    base_prices = []
    discounts = []
    for page in range(0, int(pages)):
        with open(
            os.getcwd() + "\\data\\" + str(category) + "\\page_" + str(page) + ".html",
            "r",
            encoding="utf-8",
        ) as file:
            src = file.read()
            soup = BeautifulSoup(src, "lxml")
            products = soup.find("script", attrs={"id": "__NEXT_DATA__"})
            for item in products:
                python_obj = json.loads(item)
                products = python_obj["props"]["initialReduxState"]["productsList"][
                    "products"
                ]
                for product in products:
                    title = product["title"]  # название
                    id = product["id"]  # код товара
                    barcode = product["barcode"]["value"]  # штрих-код товара
                    try:
                        brand = product["brand"]["name"]  # название бренда
                    except ValueError:
                        brand = ""  # название бренда
                        pass
                    try:
                        manufacturer = product["manufacturer"]["name"]  # производитель
                    except ValueError:
                        manufacturer = ""  # название бренда
                        pass
                    offer_price = product["offer_price"]  # цена со скидкой
                    base_price = product["base_price"]  # цена без скидки
                    discount = round(
                        (1 - int(offer_price) / int(base_price)) * 100
                    )  # дисконт

                    titles.append(title)
                    ids.append(id)
                    brands.append(brand)
                    barcodes.append(barcode)
                    manufacturers.append(manufacturer)
                    offer_prices.append(offer_price)
                    base_prices.append(base_price)
                    discounts.append(discount)
    df = pd.DataFrame(
        {
            "ID": ids,
            "Title": titles,
            "Brand": brands,
            "Barcode": barcodes,
            "Manufacturer": manufacturers,
            "Offer_price": offer_prices,
            "Base_price": base_prices,
            "Discount": discounts,
        }
    )
    df.to_csv(
        "data\\" + str(category) + "\\" + str(category) + ".csv",
        index=False,
        encoding="utf-8-sig",
    )


if __name__ == "__main__":
    cat = category
    numofpages = npages

    browser = Browser()

    for i in range(0, int(numofpages)):
        browser.get_data(page=i, category=cat, website_url=website)
    browser.driver_close()

    Soup(category=cat, pages=numofpages)
