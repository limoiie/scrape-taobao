import logging

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def fetch_item_page(driver: WebDriver, url: str):
    driver.get(url)
    _detect_validation_and_skip_it(driver)
    return driver.page_source


def _detect_validation_and_skip_it(_: WebDriver):
    # it seems no need to handle it as the page can still be fetched
    pass
