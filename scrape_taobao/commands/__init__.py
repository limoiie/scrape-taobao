import logging
import os

logger = logging.getLogger("scrape-taobao")
PAGES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../cache/pages")
)
ITEMS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../cache/items")
)
