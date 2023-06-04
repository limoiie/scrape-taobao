import dataclasses
import os

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from scrape_taobao.commands import ITEMS_DIR, PAGES_DIR, logger
from scrape_taobao.core.fetch_item_page import fetch_item_page
from scrape_taobao.core.hack import hide_browser_features, prompt_and_login
from scrape_taobao.core.parse_item_page import parse_item_page
from scrape_taobao.io import dump


def scrape_one(
    url: str,
    *,
    out_dir: str = ITEMS_DIR,
    pages_dir: str = PAGES_DIR,
    fmt: str = "yaml",
    download_only: bool = False,
    no_cache: bool = False,
):
    """
    抓取商品页面，并解析商品信息。

    :param url: 商品链接列表文件，每行一个链接
    :param out_dir: 输出目录，默认为 '<project-root>/cache/items'
    :param pages_dir: 页面源码目录，默认为 '<project-root>/cache/pages'
    :param fmt: 输出格式，支持 'json' 和 'yaml'
    :param download_only: 是否只下载页面源码，不解析
    :param no_cache: 是否跳过缓存，即不使用已下载的页面源码
    """

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    with webdriver.Chrome() as driver:
        hide_browser_features(driver)
        prompt_and_login(driver)

        try:
            scrape_one_impl(
                url,
                driver,
                out_dir=out_dir,
                pages_dir=pages_dir,
                fmt=fmt,
                download_only=download_only,
                no_cache=no_cache,
            )

        except Exception as e:
            logger.exception('failed to scrape "{}": {}'.format(url, e))


def scrape_one_impl(
    url: str,
    driver: WebDriver,
    *,
    out_dir: str = ITEMS_DIR,
    pages_dir: str = PAGES_DIR,
    fmt: str = "yaml",
    download_only: bool = False,
    no_cache: bool = False,
):
    """
    Scrape a single item page from the given url.

    See also the docstring of `scrape_one`.
    """
    item_id = url[url.index("id=") :]
    page_filepath = os.path.join(pages_dir, "{}.html".format(item_id))
    out_filepath = os.path.join(out_dir, "{}.{}".format(item_id, fmt))

    # skip if item file exists
    if not no_cache and os.path.exists(out_filepath):
        logger.info('skip scrape "{}" as existing'.format(item_id))
        return

    # skip if page source file exists
    if not no_cache and os.path.exists(page_filepath):
        # load page source
        page_source = open(page_filepath).read()

        logger.info('skip fetch "{}" as existing'.format(item_id))

    else:
        try:
            # fetch page source
            page_source = fetch_item_page(driver, url)
        except Exception as e:
            logger.exception('failed to fetch "{}": {}'.format(url, e))
            raise

        logger.info('fetched "{}" - {}'.format(item_id, driver.title))

        if not no_cache:
            with open(page_filepath, "w+") as f:
                f.write(page_source)

    if not download_only:
        try:
            # parse page source
            item = parse_item_page(page_source)
        except Exception as e:
            logger.exception('failed to parse "{}": {}'.format(url, e))
            raise

        dump(dataclasses.asdict(item), out_filepath, fmt=fmt)
