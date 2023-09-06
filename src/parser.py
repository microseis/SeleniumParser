from dataclasses import dataclass
import pandas as pd
from bs4 import BeautifulSoup
import json
import os


@dataclass
class Soup:
    titles: list = None
    ids: list = None
    barcodes: list = None
    brands: list = None
    manufacturers: list = None
    offer_prices: list = None
    base_prices: list = None
    discounts: list = None

    def get_data_from_page(self, category_id: int, page_num: int):
        with open(
            os.getcwd()
            + "\\data\\"
            + str(category_id)
            + "\\page_"
            + str(page_num)
            + ".html",
            "r",
            encoding="utf-8",
        ) as file:
            src = file.read()
            parsed_data = BeautifulSoup(src, "lxml")
            products = parsed_data.find("script", attrs={"id": "__NEXT_DATA__"})
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

                    self.titles.append(title)
                    self.ids.append(id)
                    self.brands.append(brand)
                    self.barcodes.append(barcode)
                    self.manufacturers.append(manufacturer)
                    self.offer_prices.append(offer_price)
                    self.base_prices.append(base_price)
                    self.discounts.append(discount)

    def parse_website(self, category: int, pages: int) -> None:
        for page in range(0, int(pages)):
            self.get_data_from_page(category_id=category, page_num=page)

        df = pd.DataFrame(
            {
                "id": self.ids,
                "title": self.titles,
                "brand": self.brands,
                "barcode": self.barcodes,
                "manufacturer": self.manufacturers,
                "offer_price": self.offer_prices,
                "base_price": self.base_prices,
                "discount": self.discounts,
            }
        )
        df.to_csv(
            "data\\" + str(category) + "\\" + str(category) + ".csv",
            index=False,
            encoding="utf-8-sig",
        )
