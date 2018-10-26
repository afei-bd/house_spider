# House Spider 

House spider是一个简单的爬虫脚本，利用Selenium/BeautifulSoup/Chrome Webdriver爬取链家网上的房源信息。

## Version

*NEW: version 1.0.0 (2018-10-07) birthday of house spider!*

## Introduction

### 为什么会有House spider？

最近准备买二手房，看房和跟房主沟通的过程中有一些疑问，不知道这个小区的房子好不好，房主的这套房子热不热？竞争的人多不多？了解这些信息，对进行二手房源的选择，以及价格谈判非常重要。

在链家的官网上，有几个重要的信息：小区的成交均价、成交单价、在售房源数量、带看量、成交量等。受限于政策的影响，小区整体成交均价及单价仅具备参考价值，对某一套房源来讲意义不大。如满五与满二的房源、公房与商品房等，税费方面存在较大差异。

那么怎么判断房屋的价值，以及市场热度呢？客户是用脚来投票的，一个房子的关注度、带看量（7天带看/30天带看）等信息是可以反馈房源的热度的。比如某套房近7天有20次带看，说明关注的中介及客户很多，竞争可能会比较激烈，如果有意的话，动作需要迅速点。

### House spider能干啥？

House spider能够爬取指定小区的房源信息，并进行关注度、带看量统计。目前House spider能做的比较有限，但基于House spider，可以进行天级的抓取和监控，分析指定小区或房源的热度。

## Dependency

House spider是一个爬虫工具，依赖以下第三方工具：

1. Selenium: Selenium [1] 是一个用于Web应用程序测试的工具。Selenium测试直接运行在浏览器中，就像真正的用户在操作一样。在House spider里，利用Selenium模拟网页的翻页、点击等行为，访问小区的搜索结果列表页及详情页。

    selenium安装: 

    $ pip install selenium

2. BeautifulSoup: Beautiful Soup [2] 是一个可以从HTML或XML文件中提取数据的Python库.它能够通过你喜欢的转换器实现惯用的文档导航。House spider利用Beautiful Soup解析HTML页面中特点的节点元素，来提取目标数据信息。

    BeautifulSoup安装: 

    $ pip install BeautifulSoup


3. Chrome Webdriver: WebDriver顾名思义，是用来drive web browser的。chrome webdriver是用来驱动chrome执行自动化测试的。使用Chrome webdriver需要与Chrome浏览器的版本对应 [4]。

    Windows Chrome Webdriver安装与配置: https://www.jianshu.com/p/5ea69cd6c3f5

    MacOS Chrome Webdriver安装与配置: https://www.jianshu.com/p/e137031bc7db

## How to use?

### 启动

    python house_spider.py -c conf.ini

### 配置说明

    [spider]  
    query_list: ./query_list  小区名称（精确匹配）
    host: https://m.lianjia.com/bj/ershoufang/rs （抓取url前缀）

    [webdriver] 
    headless: 1   （是否隐藏抓取浏览器窗口，0:不隐藏，1:隐藏）
    script_timeout: 10  （js超时设置）
    page_load_timeout: 20 （页面加载超时设置）
    image: 0       （是否加载图片，0:不加载，1:加载）

### 输出说明

输出文件位置: ./output/

detail信息: 当日在售房源信息，存储位置：./output/$day/$小区名称，格式：

    url \t 总价 \t 房型 \t 面积 \t 单价 \t 挂牌时间 \t 朝向 \t 楼层 \t 7天带看 \t 30天带看 \t 收藏人数 

daily diff信息: 该小区与昨天相比，房源信息的变化情况，包括房源新增、下线、涨价与降价，存储位置：./output/$day/diff.info，格式：

    小区名称 \t day1 vs day2 \t 新增房源:$num1 \t 下线房源:$num2 \t 涨价房源:$num3 \t 降价房源:$num4
    新增 \t 房源信息
    下线 \t 房源信息
    降价 \t 房源信息
    涨价 \t 房源信息

static信息: 待爬取小区的汇总统计信息，./output/$小区名称，格式:
    
    时间 \t 在售房源数 \t  7天带看 \t 30天带看 \t 收藏人数

[1]:	https://www.seleniumhq.org/
[2]:    https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html
[3]:    https://docs.seleniumhq.org/projects/webdriver/
[4]:    https://blog.csdn.net/huilan_same/article/details/51896672
