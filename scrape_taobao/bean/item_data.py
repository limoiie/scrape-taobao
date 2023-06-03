import dataclasses
from typing import List, Tuple


@dataclasses.dataclass
class ItemChoiceData:
    # 属性标签 ID
    tags: List[str]
    # 属性标签名称
    name: str
    # 库存单位 ID
    sku_id: str
    # 价格
    price: float
    # 库存
    stock: int
    # 是否售罄
    oversold: bool


@dataclasses.dataclass
class ItemData:
    # 商品平台，taobao 或者 tmall
    platform: str
    # 商品标题
    title: str
    # 商品详情
    details: dict
    # 配送信息
    delivery_info: str
    # 商品类别
    choices: List[ItemChoiceData]
    # 价格范围
    price_range: Tuple[float, float]
    # 总库存
    total_stock: int
    # 月度总销量
    sales: int
