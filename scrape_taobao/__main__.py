"""
Scrape taobao items pages.
"""
import logging

import fire

from scrape_taobao.commands.filtor import filtor
from scrape_taobao.commands.parse import parse
from scrape_taobao.commands.parse_one import parse_one
from scrape_taobao.commands.scrape import scrape
from scrape_taobao.commands.scrape_one import scrape_one

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    fire.Fire(
        dict(
            scrape=scrape,
            scrape_one=scrape_one,
            parse=parse,
            parse_one=parse_one,
            filter=filtor,
        )
    )
