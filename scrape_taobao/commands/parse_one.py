import dataclasses
import os

from scrape_taobao.commands import ITEMS_DIR, logger
from scrape_taobao.core.parse_item_page import parse_item_page
from scrape_taobao.io import dump


def parse_one(page_path: str, *, out_dir: str = ITEMS_DIR, fmt: str = "yaml"):
    """
    解析一个商品页面。

    如果想要下载源页面并解析，可以使用 `scrape-one` 命令。

    :param page_path: 页面源码文件
    :param out_dir: 商品信息文件所在目录，默认为 '<project-root>/cache/items'
    :param fmt: 商品信息文件格式，支持 'json' 和 'yaml'
    """
    os.makedirs(out_dir, exist_ok=True)

    try:
        parse_one_impl(page_path, out_dir=out_dir, fmt=fmt)
    except Exception as e:
        logger.exception('failed to parse "{}": {}'.format(page_path, e))


def parse_one_impl(page_path: str, out_dir: str = ITEMS_DIR, fmt: str = "yaml"):
    """
    Parse one item page.

    See also the docstring of `parse_one`.
    """
    with open(page_path, "r") as f:
        item_data = parse_item_page(f)

    out_filename = os.path.basename(page_path).replace(
        ".html", ".{}".format(fmt)
    )
    out_path = os.path.join(out_dir, out_filename)
    dump(dataclasses.asdict(item_data), out_path, fmt=fmt)
