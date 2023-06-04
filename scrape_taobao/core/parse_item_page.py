import json
import re
from json import JSONDecodeError
from typing import List, TextIO, Union

import bs4

from scrape_taobao.bean.item_data import ItemChoiceData, ItemData


def parse_item_page(page_source: Union[str, TextIO]) -> ItemData:
    page = bs4.BeautifulSoup(page_source, "html.parser")

    if "tmall.com" in page.title.string:
        data = TMallItemPageParser(page).parse()
    else:
        data = TaobaoItemPageParser(page).parse()

    return data


# regex templates for taobao
RX_SKU = re.compile(r"skuMap\s*:(?P<map>[^\n]*)$", re.MULTILINE)
RX_MEM = re.compile(r"propertyMemoMap\s*:(?P<map>[^\n]*)$", re.MULTILINE)

# regex templates for tmall
RX_ITEM_HEADER_SALES_DESC = re.compile(r"ItemHeader--salesDesc--.*")
RX_ITEM_DETAIL_ATTRS = re.compile(r"ItemDetail--attrs--.*")
RX_ATTRS_ATTR = re.compile(r"Attrs--attr--.*")
RX_PRICE_PRICE_TEXT = re.compile(r"Price--priceText--.*")


class TMallItemPageParser:
    def __init__(self, page: bs4.BeautifulSoup):
        self.page = page

    def parse(self):
        choices = self.extract_choices()

        return ItemData(
            platform="tmall",
            title=self.page.title.text,
            details=self.extract_details(),
            delivery_info=self.extract_delivery_info(),
            choices=choices,
            price_range=self.extract_price_range(choices),
            total_stock=self.extract_total_stock(choices),
            sales=self.extract_sales(),
        )

    def extract_details(self):
        details = {}

        attrs = self.page.find("div", class_=RX_ITEM_DETAIL_ATTRS)
        if attrs is None:
            return details

        for attr in attrs.find_all("span", class_=RX_ATTRS_ATTR):
            label, value = attr.text.split("：")
            details[label.strip()] = value.strip()
        return details

    def extract_delivery_info(self):
        delivery_info = self.page.find("div", class_="delivery-info")
        if delivery_info:
            return ";".join(
                span.text for span in delivery_info.find_all("span")
            )
        return "-"

    @staticmethod
    def extract_choices():
        # TODO
        return []

    def extract_price_range(self, _: List[ItemChoiceData]):
        price = self.page.find("span", class_=RX_PRICE_PRICE_TEXT)
        if price:
            # TODO: the max price is not shown in tmall
            return float(price.text), float(price.text)

        return 0.0, 0.0

    @staticmethod
    def extract_total_stock(_: List[ItemChoiceData]):
        # TODO: the total stock is not shown in tmall
        return 0

    def extract_sales(self):
        sales_desc = self.page.find("span", class_=RX_ITEM_HEADER_SALES_DESC)
        if sales_desc:
            match = re.search(r"\d+", sales_desc.text)
            if match:
                number = int(match.group())
                return number

        return 0


class TaobaoItemPageParser:
    def __init__(self, page: bs4.BeautifulSoup):
        self.page = page

    def parse(self):
        choices = self.extract_choices()

        return ItemData(
            platform="taobao",
            title=self.page.title.text,
            details=self.extract_details(),
            delivery_info=self.extract_delivery_info(),
            choices=choices,
            price_range=self.extract_price_range(choices),
            total_stock=self.extract_total_stock(choices),
            sales=self.extract_sales(),
        )

    def extract_details(self):
        details = {}

        attrs = self.page.find("ul", class_="attributes-list")
        if attrs is None:
            return details

        for attr in attrs.find_all("li"):
            label, value = attr.text.split(":")
            details[label.strip()] = value.strip()
        return details

    def extract_delivery_info(self):
        delivery_days = self.page.find(id="J_ServiceMarkInfo")
        return delivery_days.text.strip() if delivery_days else "-"

    def extract_choices(self):
        choices = []
        page_source = str(self.page)
        sku_m = RX_SKU.search(page_source)
        mem_m = RX_MEM.search(page_source)

        if not sku_m or not mem_m:
            return choices

        (sku_str,) = sku_m.groups()
        (mem_str,) = mem_m.groups()

        try:
            sku: dict = json.loads(sku_str)
            mem: dict = json.loads(mem_str)
        except JSONDecodeError:
            return choices

        for seq, attrs in sku.items():
            tags = list(filter(None, seq.split(";")))
            for tag in tags:
                if tag in mem:
                    name = mem.get(tag)
                    break

            else:
                name = "-"

            choices.append(
                ItemChoiceData(
                    tags=tags,
                    name=name,
                    sku_id=attrs.get("skuId") or "-",
                    price=float(attrs.get("price") or "-1."),
                    stock=int(attrs.get("stock") or "-1"),
                    oversold=attrs.get("oversold") or False,
                )
            )

        return choices

    def extract_price_range(self, sub_items: List[ItemChoiceData]):
        if sub_items:
            prices = [c.price for c in sub_items]
            return min(prices), max(prices)

        price = self.page.find(id="J_StrPrice")
        if price:
            price_range = price.find("em", class_="tb-rmb-num")
            prices = [float(p.strip()) for p in price_range.text.split("-")]
            return min(prices), max(prices)

        return 0.0, 0.0

    def extract_total_stock(self, sub_items: List[ItemChoiceData]):
        if sub_items:
            return sum(c.stock for c in sub_items)

        stock = self.page.find(id="J_SpanStock")
        return int(stock.text) if stock else 0

    def extract_sales(self):
        sell_counter = self.page.find(id="J_SellCounter")
        return int(
            sell_counter.text
            if sell_counter and sell_counter.text not in ["-", ""]
            else "0"
        )
