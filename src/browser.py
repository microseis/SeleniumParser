import os

from src.config import app_settings
from src.logger import logger
import pickle
import time


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=self.options
        )
        self.directory = ""

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

    def get_data(self, page: int):
        """Метод получения данных для выбранной категории и страницы."""
        self.directory = os.getcwd() + "\\data\\" + str(app_settings.category) + "\\"

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.get_driver()
        try:
            self.driver.get(
                url=app_settings.website_name
                + str(app_settings.category)
                + "?page="
                + str(page)
            )
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
            logger.info(ex)

    def driver_close(self) -> None:
        self.driver.close()
        self.driver.quit()
