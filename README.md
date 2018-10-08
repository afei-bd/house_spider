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

目前House spider能做的比较有限，只能爬取指定小区的房源信息，并进行关注度、带看量统计。基于House spider，可以进行天级的抓取和监控，分析指定小区或房源的热度。

## Dependency

House spider是一个爬虫工具，依赖以下第三方工具：

1. Selenium: Selenium [1]  是一个用于Web应用程序测试的工具。Selenium测试直接运行在浏览器中，就像真正的用户在操作一样。House spider利用Selenium进行网页的翻页、点击等模拟行为

2. BeautifulSoup: 

3. Chrome Webdriver: 

[1]:	https://www.seleniumhq.org/