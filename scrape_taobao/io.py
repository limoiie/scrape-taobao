import json
import random
import sys
from contextlib import nullcontext
from typing import Optional

import yaml


def dump(data: dict, out_path: Optional[str], fmt: str):
    """
    Dump data to file or stdout.

    :param data: data to dump
    :param out_path: output file path, if None, dump to stdout
    :param fmt: output format, support 'json' and 'yaml'
    """
    stream_guard = open(out_path, "w+") if out_path else nullcontext(sys.stdout)
    with stream_guard as stream:
        if fmt == "json":
            json.dump(
                data, stream, ensure_ascii=False, indent=2, sort_keys=False
            )
        elif fmt in ["yaml", "yml"]:
            yaml.dump(
                data, stream, allow_unicode=True, indent=2, sort_keys=False
            )
        else:
            raise ValueError("unsupported format: {}".format(fmt))


def load_item_list(item_list: str, n=-1, shuffle=False):
    """
    Load item urls from file.

    :param item_list: item list file path
    :param n: number of items to load, -1 means load all items
    :param shuffle: whether to shuffle the item urls
    """
    with open(item_list) as f:
        item_urls = list(url.strip() for url in f.readlines())
    random.shuffle(item_urls) if shuffle else None
    item_urls = item_urls[:n]
    return item_urls
