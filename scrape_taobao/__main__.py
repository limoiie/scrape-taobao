"""
Scrape taobao items pages.
"""
import dataclasses
import glob
import logging
import os
import random

import fire
from selenium import webdriver

from scrape_taobao.core.fetch_item_page import fetch_item_page
from scrape_taobao.core.hack import hide_browser_features, prompt_and_login
from scrape_taobao.core.parse_item_page import parse_item_page
from scrape_taobao.dumps import dump
from scrape_taobao.utils import fake_pause

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrape-taobao")

PAGES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../db/pages")
)


def fetch(
    items: str, pages_dir: str = PAGES_DIR, n: int = -1, shuffle: bool = True
):
    """
    从商品链接列表中抓取商品页面。

    :param items: 商品链接列表文件，每行一个链接
    :param pages_dir: 页面源码目录，默认为 '<project-root>/db/pages'
    :param n: 抓取商品数量，默认抓取全部商品
    :param shuffle: 是否打乱商品链接列表
    """

    os.makedirs(pages_dir, exist_ok=True)

    # load item urls from file
    with open(items) as f:
        item_urls = list(url.strip() for url in f.readlines())
    item_urls = random.shuffle(item_urls) if shuffle else item_urls
    item_urls = item_urls[:n]

    with webdriver.Chrome() as driver:
        hide_browser_features(driver)
        prompt_and_login(driver)

        while item_urls:
            url = item_urls.pop()
            try:
                fetch_item_page(driver, url, pages_dir)
            except Exception as e:
                logger.exception('failed to fetch "{}": {}'.format(url, e))
                item_urls.append(url)

            fake_pause()


def parse(
    out_dir: str = None,
    pages_dir: str = PAGES_DIR,
    fmt: str = "yaml",
    force=False,
):
    """
    从页面源码文件中解析出商品信息。

    :param out_dir: 输出目录，默认输出到控制台
    :param pages_dir: 页面源码目录，默认为 '<project-root>/db/pages'
    :param fmt: 输出格式，支持 'json' 和 'yaml'，默认为 'yaml'
    :param force: 是否强制解析所有页面，默认只解析未解析过的页面
    """

    os.makedirs(pages_dir, exist_ok=True)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for page_filepath in glob.glob(os.path.join(pages_dir, "id=*.html")):
        page_basename = os.path.basename(page_filepath).replace(
            ".html", ".{}".format(fmt)
        )

        out_filepath = os.path.join(out_dir, page_basename) if out_dir else None
        if not force and out_filepath and os.path.exists(out_filepath):
            logger.info('skip "{}"'.format(out_filepath))
            continue

        data = parse_item_page(page_filepath)

        dump(dataclasses.asdict(data), out_filepath, fmt=fmt)


if __name__ == "__main__":
    fire.Fire(dict(fetch=fetch, parse=parse))
