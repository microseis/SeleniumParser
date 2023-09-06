from src.browser import Browser
from src.config import app_settings
from src.parser import Soup


if __name__ == "__main__":
    browser = Browser()

    soup = Soup()

    for i in range(0, app_settings.numpages):
        browser.get_data(page=i)
    browser.driver_close()

    soup.parse_website(category=app_settings.category, pages=app_settings.num_pages)
