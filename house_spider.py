#!/usr/bin/env python
# encoding=utf8  

"""
Date:    2017/12/05
"""
import os
import logging
import logging.handlers
import argparse
import json
import urllib2
import urlparse
from bs4 import BeautifulSoup
import HTMLParser
import re
from selenium import webdriver
import time
import ConfigParser
import datetime

import sys
reload(sys)
sys.setdefaultencoding("utf8")

log_format = "%(asctime)s: %(levelname)s: %(filename)s:%(lineno)d * %(threadName)s %(message)s"
log_date_format = "%m-%d %H:%M:%S"

__version__ = "mini_spider 1.0.0.0"
__usage__ = ""
counter = 1
speed = 20
MAX_PAGE = 4
DATA_LEN = 7

def show_version():
    print __version__

def show_usage():
    print __usage__

def init_log(path, level=logging.INFO, split_mode="D", backup_num=7,
    fmt=log_format, date_fmt=log_date_format):

    formatter = logging.Formatter(fmt, date_fmt)
    logger = logging.getLogger()
    logger.setLevel(level)

    log_dir = os.path.dirname(path)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    hd_info = logging.handlers.TimedRotatingFileHandler(path + ".log",
                when=split_mode,
                backupCount=backup_num)
    hd_info.setLevel(level)
    hd_info.setFormatter(formatter)
    logger.addHandler(hd_info)

    hd_warn = logging.handlers.TimedRotatingFileHandler(path + ".log.wf",
                when=split_mode,
                backupCount=backup_num)
    hd_warn.setLevel(logging.WARNING)
    hd_warn.setFormatter(formatter)
    logger.addHandler(hd_warn)

    return logger

def parser_config(config_file, config_dict):
	""" Check config file """
	#print config_file
	logging.info("loading config file %s" % (config_file) )
	if config_file is None or not os.path.isfile(config_file):
		logging.error("config file %s not find" % (config_file) )
		return -1

	cf = ConfigParser.ConfigParser()
	cf.read(config_file)
	if not cf.has_section("spider"):
		logging.error("config format error: cannot find section spider!")
		return -1

	"""
	Config file format:

	[spider] 
	query_list: ./query        ; seed file path
	host: https://**.**        ; output directory 

    [webdrvier]
	headless: 1                ; max crawl depth 
	ua: 1                      ; crawl time interval (second)
	"""

	""" url list file """
	try:
		config_dict["query_list"] = cf.get("spider", "query_list")
	except ConfigParser.NoOptionError as error:
		# default url list file
		if os.path.isfile("./query_list"):	
			config_dict["query_list"] = "./query_list"
		else:
			logging.error("cannot find crawl query list!")
			return -1

	""" host url """
	try:
		config_dict["host"] = cf.get("spider", "host")
	except ConfigParser.NoOptionError as error:
		config_dict["host"] = "https://m.lianjia.com/bj/ershoufang/"

	""" output dir """
	try:
		config_dict["output_dir"] = cf.get("spider", "output_dir")
	except ConfigParser.NoOptionError as error:
		config_dict["output_dir"] = "./output"

	if not os.path.exists(config_dict["output_dir"]):
		os.makedirs(config_dict["output_dir"])

	""" thread count """
	try:
		config_dict["thread_count"] = cf.getint("spider", "thread_count")
		# check thread count conf
		if config_dict["thread_count"] <= 0:
			logging.info("config thread count error!")
			config_dict["thread_count"] = 8
	except ConfigParser.NoOptionError as error:
		config_dict["thread_count"] = 8

	return 0

def get_host(url):
    proto, rest = urllib2.splittype(url)
    host, rest = urllib2.splithost(rest) 
    return None if not host else host 

def parser_visit_detail(url, driver):
    detail_list = []

    ## driver load url
    try:
        logging.info("get url: %s by webdriver" %(url))
        driver.get(url)
    except Exception as e:
        logging.error("get url %s failed, err_msg=%s!" % (url, e))
        return None
    
    try:
        content = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        logging.error("get page source failed, err_msg=%s!" % (e))
        return None

    try:
        ## parser house desc
        house_desc = content.find_all("div", {"class":"similar_data_detail"})
        for item in house_desc:
            detail_list.append( (item.find_all("p", {"class":"red big"}))[0].get_text() )

        ## parser house info
        li_info = content.find_all("li", {"class":"short"})
        li_list = []
        for li in li_info:
            li_list.append(li.get_text())
        
        detail_list.extend(li_list[:4])

        ## parser visit info
        dat_info = content.find_all("div", {"class":"data flexbox"})
        box_info = dat_info[0].find_all("div", {"class":"box_col"})
        for box in box_info:
             detail_list.append((box.find_all("strong"))[0].get_text())

    except Exception as e:
        logging.error("get url %s failed, err=%s!" % (url, e))
        return None
    
    return detail_list

def save(content, save_file):
    """ Open file and save """
    try:
        save_fp = open(save_file, "a+")
        save_fp.write(content)
        save_fp.close()
        logging.info("save %s to output dir: %s." % (content, save_file))
    except Exception as e:
		logging.error("save url: %s failed, error msg: %s!" % (content, e))

def parser_house_by_selenium(prefix, query, driver, save_dir):
    ## step 1: make url by host and query, and save file
    url = prefix + query
    detail_save_file = save_dir + "/" + query
    commu_save_file  = save_dir + "/../" + query

    ## 
    if os.path.exists(detail_save_file):
        return

    ## step 2: open url by chrome driver 
    try:
        logging.info("get url: %s by webdriver" %(url))
        driver.get(url)
    except Exception:
        logging.error("get url %s failed!" % (url))
        return
    
    ## step 3: scroll MAX_PAGE times to get all item list
    for i in range(MAX_PAGE):
        scrol_len = (i+1) * 5000
        js="var q=document.documentElement.scrollTop="+str(scrol_len)
        logging.info("scrolling to %d" %(scrol_len))
        driver.execute_script(js)
        time.sleep(2)
    
    ## step 4: get host url
    host = get_host(url)

    ## step 5: get content by btsoup
    content = BeautifulSoup(driver.page_source, "html.parser")
    houselist = content.findAll("li", {"class":"pictext"})
    ## parser house info
    total_house  = 0
    visit_7_day  = 0
    visit_30_day = 0
    all_follower = 0
    commu_info = list()
    for house in houselist:
        detail_url = (house.find_all('a'))[0].get('href')
        detail_url = "https://"+host+detail_url
        #print detail_url
        detail = parser_visit_detail(detail_url, driver)
        if detail != None and len(detail) > 0:
            ## static info
            total_house  += int(1)
            visit_7_day  += int(detail[-3])
            visit_30_day += int(detail[-2])
            all_follower += int(detail[-1])

            output_str = detail_url + "\t" + '\t'.join(detail)
            print '  '.join(detail)
            save(output_str+"\n", detail_save_file)

    ## print and save commu info
    commu_info.append(datetime.datetime.now().strftime('%Y%m%d'))
    commu_info.append("在售房源:"+str(total_house))
    commu_info.append("近7日带看:"+str(visit_7_day))
    commu_info.append("30日带看:"+str(visit_30_day))
    commu_info.append("关注人数:"+str(all_follower))
    save('\t'.join(commu_info)+"\n", commu_save_file)
    #print '\t'.join(commu_info)

def read_file(file_dir):
    file_info = list()
    try:
        file_fp = open(file_dir)
        for line in file_fp:
            line = line.strip('\n').split('\t')
            house_id = (re.findall(r"(.*)?/(.+).html", line[0]))[0][1]
            newline  = [ house_id ] + line
            #print newline
            ## key : house id \t house info
            file_info.append(newline)
        file_fp.close()
    except Exception as err:
        logging.error("read file %s error, msg=%s" %(file_dir, err))
    
    return file_info

def find_elem(item, src_list):
    for elem in src_list:
        if item in elem:
            return elem
    return list()

def get_price(str):
    return str[:-6]

def get_daily_diff(query, file_dir):
    ## get today data
    cur_day  = datetime.date.today().strftime('%Y%m%d')
    cur_file = file_dir + "/" + cur_day + "/" + query
    if not os.path.exists(cur_file):
        logging.error("%s file does not exist!" %(cur_file))
        return
    
    save_file = file_dir + "/" + cur_day + "/" + "diff.info"
    
    ## find last data in last DATA_LEN days
    last_day  = ""
    last_file = ""
    find_flag = False
    for i in range(1,DATA_LEN):
        last_day  = (datetime.date.today() - datetime.timedelta(days=i))
        last_file = file_dir + "/" + last_day.strftime('%Y%m%d') + "/" + query
        if os.path.exists(last_file):
            logging.info("find file: %s" %(last_file))
            find_flag = True
            break
    
    if find_flag == False:
        logging.warn("cannot find data of %s in last week" %(query))
        return
    
    ## comparing data
    logging.info("compare %s data of %s and %s" %(query, cur_day, last_day))
    cur_data  = read_file(cur_file)
    last_data = read_file(last_file)

    ## find new info
    new_data = list()
    price_up = list()
    price_dn = list()
    for elem in cur_data:
        house_id  = elem[0]
        price_new = get_price(elem[2])
        match_res = find_elem(house_id, last_data)
        if len(match_res) <= 0:
            new_data.append(elem)
        else:
            price_old = get_price(match_res[2])
            price_str = [price_old+"=>"+price_new]
            if price_new > price_old:
                price_up.append(elem + price_str)
            elif price_new < price_old:
                price_dn.append(elem + price_str)

    ## find del info
    del_data = list()
    for elem in last_data:
        house_id  = elem[0]
        match_res = find_elem(house_id, cur_data)
        if len(match_res) <= 0:
            del_data.append(elem)
    
    ## save result and print result
    save_info = query + '\t' + str(cur_day)  + " vs " + str(last_day)
    save_info = save_info + '\t' + "新增房源: " + str(len(new_data))
    save_info = save_info + '\t' + "下线房源: " + str(len(del_data))
    save_info = save_info + '\t' + "涨价房源: " + str(len(price_up))
    save_info = save_info + '\t' + "降价房源: " + str(len(price_dn))
    save_info = save_info + '\n'
    for item in new_data:
        save_info = save_info + "新增\t" + '\t'.join(item[1:]) + '\n'

    for item in del_data:
        save_info = save_info + "下线\t" + '\t'.join(item[1:]) + '\n'

    for item in price_up:
        save_info = save_info + "涨价(" + item[-1] + ")\t" + '\t'.join(item[1:-1]) + '\n'

    for item in price_dn:
        save_info = save_info + "降价(" + item[-1] + ")\t" + '\t'.join(item[1:-1]) + '\n'
    
    save_info = save_info + '\n' 
    save(save_info, save_file)

    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="store_true", help="show version")
    parser.add_argument("-c", "--config", help="config file")
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()
    
    """ Show version """
    if args.version:
        show_version()
        sys.exit(0)
    
    """ Parser config """

    """ Initial webdriver """
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options = options)
    driver.set_script_timeout(10)
    driver.set_page_load_timeout(20)
    
    """ Initial log """
    (filename, ext) = os.path.splitext(sys.argv[0])
    logger = init_log(sys.path[0]+"/log/"+filename)

    """ Parser config file """
    conf_dict = {}
    if parser_config(args.config, conf_dict) < 0:
        logger.error("parser config %s failed!" %(args.config) )
        sys.exit(-1)

    """ save dir """
    cur_day  = datetime.datetime.now().strftime('%Y%m%d')
    save_dir = conf_dict["output_dir"] + "/" + cur_day
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    """ read url file and put to the queue """
    query_list = open(conf_dict["query_list"])
    url_host   = conf_dict["host"]    
    for line in query_list:
        ## skip comment line and empty line
        if not len(line) or line.startswith("#"):
            logging.info("skip line: %s" %(line.strip()))
            continue

        # print url, save_file
        parser_house_by_selenium(url_host, line.strip(), driver, save_dir)

        # post process, calculate daily diff
        get_daily_diff(line.strip(), conf_dict["output_dir"])
    
    driver.quit()


    return 0

if __name__ == '__main__':
    main()