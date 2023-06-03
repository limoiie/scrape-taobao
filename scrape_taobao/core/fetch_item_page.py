import logging
import os

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def fetch_item_page(driver: WebDriver, url: str, pages_dir: str):
    item_id = url[url.index("id=") :]
    page_filepath = os.path.join(pages_dir, "{}.html".format(item_id))

    if os.path.exists(page_filepath):
        logger.info('skip "{}"'.format(item_id))
        return

    driver.get(url)
    detect_validation_and_skip_it(driver)

    with open(page_filepath, "w+") as f:
        f.write(driver.page_source)

    logger.info('fetched "{}" - {}'.format(item_id, driver.title))


def detect_validation_and_skip_it(_: WebDriver):
    # it seems no need to handle it as the page can still be fetched
    pass
