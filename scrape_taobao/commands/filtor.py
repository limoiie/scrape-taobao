import glob
import os

import dacite

from scrape_taobao.bean.item_data import ItemData
from scrape_taobao.commands import ITEMS_DIR, logger
from scrape_taobao.io import dump, load


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
