import glob
import os

import rich.progress

from scrape_taobao.commands import ITEMS_DIR, PAGES_DIR
from scrape_taobao.commands.parse_one import parse_one_impl


def parse(
    pages_dir: str = PAGES_DIR, out_dir: str = ITEMS_DIR, fmt: str = "yaml"
):
    """
    解析商品页面。

    该命令会解析 '<pages_dir>/*.html' 中的页面源码，抽取其中的商品信息，并将商品信息
    保存到 '<out_dir>/*.json' 或 '<out_dir>/*.yaml' 中。

    如果想要下载源页面并解析，可以使用 `scrape` 命令。

    :param pages_dir: 页面源码目录，默认为 '<project-root>/cache/pages'
    :param out_dir: 商品信息输出目录，默认为 '<project-root>/cache/items'
    :param fmt: 商品信息文件格式，支持 'json' 和 'yaml'
    """
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    page_paths = glob.glob(os.path.join(pages_dir, "id=*.html"))

    with rich.progress.Progress(transient=True) as progress:
        task_id = progress.add_task("parsing", total=len(page_paths))

        for page_path in page_paths:
            try:
                parse_one_impl(
                    page_path, out_dir=out_dir, fmt=fmt, log=progress.log
                )

            except Exception as e:
                progress.log('failed to parse "{}": {}'.format(page_path, e))
                continue

            finally:
                progress.update(task_id, advance=1)
