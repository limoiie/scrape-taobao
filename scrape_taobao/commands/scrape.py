import os

from selenium import webdriver

from scrape_taobao.commands import ITEMS_DIR, PAGES_DIR, logger
from scrape_taobao.commands.scrape_one import scrape_one_impl
from scrape_taobao.core.hack import hide_browser_features, prompt_and_login
from scrape_taobao.io import load_item_list
from scrape_taobao.utils import fake_pause


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
                logger.error('failed to scrape item "{}": {}'.format(url, e))
                failed_item_urls.append(url)

            fake_pause()
