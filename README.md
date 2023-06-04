# scrape-taobao

爬取淘宝商品信息。

本项目是一个爬取淘宝商品信息的爬虫，使用了selenium框架，爬取的信息包括商品名称、价格、销量等信息。

## 开发环境配置

### 安装 poetry

请根据官方文档安装
poetry：[Poetry - Python dependency management and packaging made easy.](https://python-poetry.org/docs/#installation)

### 安装本项目

```shell
# 创建 python 虚拟环境
poetry shell

# 安装项目依赖
poetry install

# 以开发模式安装本项目
pip install -e .
```

## 使用示例

### 爬取商品列表

从指定商品 url 列表文件中爬取商品信息，如：

```shell
python -m scrape-taobao scrape ./item-list 
```

所爬取得商品列表文件默认在`./cache/items`文件夹中，可以通过`--out-dir`参数指定，如：

```shell
python -m scrape-taobao scrape ./item-list --out-dir=./another-out-dir
```

### 爬取单个商品页面

爬取指定 url 的商品信息，如：

```shell
python -m scrape-taobao scrape-one https://item.taobao.com/item.htm?id=710127521853
```

所爬取得商品列表文件默认在`./cache/items`文件夹中，可以通过`--out-dir`参数指定，如：

```shell
python -m scrape-taobao scrape-one https://item.taobao.com/item.htm?id=710127521853 --out-dir=./another-out-dir
```

### 过滤商品信息

```shell
python -m scrape-taobao filter --min-price=200 --max-sales=1000
```

### 查看命令使用说明

查看所有命令：

```shell
python -m scrape-taobao -- --help
```

输出：

```
NAME
    __main__.py

SYNOPSIS
    __main__.py COMMAND

COMMANDS
    COMMAND is one of the following:

     scrape
       从商品链接列表中抓取商品页面，并解析商品信息。

     scrape_one
       抓取商品页面，并解析商品信息。

     parse
       解析商品页面。

     parse_one
       解析一个商品页面。

     filter
       过滤商品信息。
```

查看子命令使用说明：

```    
python -m scrape-taobao scrape -- --help
python -m scrape-taobao scrape-one -- --help
python -m scrape-taobao parse -- --help
python -m scrape-taobao parse-one -- --help
python -m scrape-taobao filter -- --help
```
