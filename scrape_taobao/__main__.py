"""
Scrape taobao items pages.
"""
import dataclasses
import glob
import logging
import os

import dacite
import fire
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from scrape_taobao.bean.item_data import ItemData
from scrape_taobao.core.fetch_item_page import fetch_item_page
from scrape_taobao.core.hack import hide_browser_features, prompt_and_login
from scrape_taobao.core.parse_item_page import parse_item_page
from scrape_taobao.io import dump, load, load_item_list
from scrape_taobao.utils import fake_pause

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrape-taobao")

PAGES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cache/pages")
)
ITEMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cache/items")
)


def scrape(
    item_list: str,
    *,
    out_dir: str = ITEMS_DIR,
    pages_dir: str = PAGES_DIR,
    fmt: str = "yaml",
    n: int = -1,
    shuffle: bool = True,
    download_only: bool = False,
    no_cache: bool = False,
):
    """
    从商品链接列表中抓取商品页面，并解析商品信息。

    :param item_list: 商品链接列表文件，每行一个链接
    :param out_dir: 输出目录，默认为 '<project-root>/cache/items'
    :param pages_dir: 页面源码目录，默认为 '<project-root>/cache/pages'
    :param fmt: 输出格式，支持 'json' 和 'yaml'
    :param n: 抓取商品数量，默认抓取全部商品
    :param shuffle: 是否打乱商品链接列表
    :param download_only: 是否只下载页面源码，不解析
    :param no_cache: 是否跳过缓存，即不使用已缓存的页面源码或解析结果
    """

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    with webdriver.Chrome() as driver:
        hide_browser_features(driver)
        prompt_and_login(driver)

        # load item urls from file
        item_urls = load_item_list(item_list, n=n, shuffle=shuffle)
        failed_item_urls = []

        while item_urls:
            url = item_urls.pop()

            try:
                _scrape_item(
                    url,
                    driver,
                    out_dir=out_dir,
                    pages_dir=pages_dir,
                    fmt=fmt,
                    download_only=download_only,
                    no_cache=no_cache,
                )

            except Exception as e:
                logger.error('failed to scrape item "{}": {}'.format(url, e))
                failed_item_urls.append(url)

            fake_pause()


def scrape_item(
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
            _scrape_item(
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


def parse(
    out_dir: str = ITEMS_DIR, pages_dir: str = PAGES_DIR, fmt: str = "yaml"
):
    """
    解析商品页面。

    该命令会解析 '<pages_dir>/*.html' 中的页面源码，抽取其中的商品信息，并将商品信息
    保存到 '<out_dir>/*.json' 或 '<out_dir>/*.yaml' 中。

    如果想要下载源页面并解析，可以使用 `scrape-taobao scrape` 命令。

    :param out_dir: 商品信息文件所在目录，默认为 '<project-root>/cache/items'
    :param pages_dir: 页面源码目录，默认为 '<project-root>/cache/pages'
    :param fmt: 商品信息文件格式，支持 'json' 和 'yaml'
    """
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    glob_pat = os.path.join(pages_dir, "*.html")

    for page_path in glob.glob(glob_pat):
        try:
            with open(page_path, "r") as f:
                item_data = parse_item_page(f)
        except Exception as e:
            logger.exception('failed to parse "{}": {}'.format(page_path, e))
            continue

        out_filename = os.path.basename(page_path).replace(
            ".html", ".{}".format(fmt)
        )
        out_path = os.path.join(out_dir, out_filename)
        dump(dataclasses.asdict(item_data), out_path, fmt=fmt)


def filtor(
    out_dir: str = ITEMS_DIR,
    *,
    fmt: str = "yaml",
    platform: str = None,
    min_price: int = None,
    max_price: int = None,
    min_total_stock: int = None,
    max_total_stock: int = None,
    min_sales: int = None,
    max_sales: int = None,
):
    """
    过滤商品信息。

    若不指定过滤选项，默认不启用对应过滤规则。

    :param out_dir: 商品信息文件所在目录，默认为 '<project-root>/cache/items'
    :param fmt: 商品信息文件格式，支持 'json' 和 'yaml'
    :param platform: 目标平台，支持 'taobao' 和 'tmall'
    :param min_price: 最低价格
    :param max_price: 最高价格
    :param min_total_stock: 最低总库存
    :param max_total_stock: 最高总库存
    :param min_sales: 最低销量
    :param max_sales: 最高销量
    """

    def filter_item(item_data: ItemData):
        if (
            min_price
            and item_data.price_range[0] != 0.0
            and item_data.price_range[0] < min_price
        ):
            return False

        if max_price and item_data.price_range[1] > max_price:
            return False

        if min_total_stock and item_data.total_stock < min_total_stock:
            return False

        if max_total_stock and item_data.total_stock > max_total_stock:
            return False

        if min_sales and item_data.sales < min_sales:
            return False

        if max_sales and item_data.sales > max_sales:
            return False

        if platform and item_data.platform not in platform:
            return False

        return True

    glob_pat = os.path.join(out_dir, "*.{}".format(fmt))

    for item_filepath in glob.glob(glob_pat):
        try:
            item_dict = load(item_filepath, fmt=fmt)
            item = dacite.from_dict(ItemData, item_dict)
        except Exception as e:
            logger.error(
                'failed to load item "{}": {}'.format(item_filepath, e)
            )
            continue

        if filter_item(item):
            # print the item data the console
            dump(item_dict, out_path=None, fmt=fmt)


def _scrape_item(
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

    See also the docstring of `scrape_item`.
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


if __name__ == "__main__":
    fire.Fire(
        dict(scrape=scrape, scrape_item=scrape_item, filter=filtor, parse=parse)
    )
