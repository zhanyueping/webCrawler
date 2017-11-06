# -*- coding:utf-8 -*-
'''
Created on 2017年9月25日

@author: ZYP
'''
from bs4 import BeautifulSoup 
from lxml import etree
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import lxml.html
import pandas as pd
import re
import time
import urllib2 
import datetime
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request,URLError
import MySQLdb as mdb

def eastMoneySecurityictWebScrapy():
    securityDict = {}
    browers = webdriver.Chrome()
    url = r"http://quote.eastmoney.com/stocklist.html"
    try:
        browers.get(url)
        securityNameSH = browers.find_elements_by_xpath("//div[@class='qox']/div[@class='quotebody']/div[@id='quotesearch']/ul/li/a")
    #     securityIDSH = browers.find_elements_by_xpath("//div[@class='qox']/div[@class='quotebody']/div[@id='quotesearch']/ul/li/a/href")
    #     securityNameSZ = browers.find_elements_by_xpath("//li/a[@name='sz']")
    #     securityIDSZ = browers.find_elements_by_xpath("//li/a[@name='sz']//@href")
        for i in xrange(len(securityNameSH)):
            if securityNameSH[i].text is not None and securityNameSH[i].get_attribute("href") is not None:
                securityIDName = str(securityNameSH[i].text.split("(")[0]).strip()
                securityIDName = securityIDName.encode("utf-8")
                securityIDTemp = str(securityNameSH[i].get_attribute("href").split(r"/")[-1].split(r".")[0]).strip()
                if 'h' in securityIDTemp:
                    securityID = "sh."+securityIDTemp[2:]
                elif 'z' in securityIDTemp:
                    securityID = "sz."+securityIDTemp[2:]
                securityDict[securityIDName] = securityID
#                 print securityIDName,"----",securityID,"------",securityIDTemp
    except Exception,e:
        print e
    return securityDict

def webWait(dr, x):
    element = WebDriverWait(dr, 2).until(
        EC.presence_of_element_located((By.XPATH, x))
    )
    return element

def clickLoadMore(browers):
    flag = True
    while  flag:
        clickLoadMore = browers.find_element_by_xpath("//div[@class='loadMore']")  
        if clickLoadMore.is_enabled():
            try:                        
                clickLoadMore.click()
                flag = False
            except Exception,e:
                print "loadMore happened Error:",e
                time.sleep(1)
        else:
            print "--clickLoadMore-not enabled---"
            time.sleep(1)
    time.sleep(2)  

def clickShowMore(browers):
    clickElement = browers.find_elements_by_xpath("//li[@class='clearfix']/div[2]/div[2]/a[@class='showMoreStock']")
                    
    i = 0
    while i < len(clickElement):
        element =  clickElement[i];
        if clickElement[i].is_enabled():
            try:
                webWait(browers,"//li[@class='clearfix']/div[2]/div[2]/a[@class='showMoreStock']")
                if len(element.text) != 0:
                    element.click()               
                i = i+1
                time.sleep(2)
            except Exception,e:
                print "showMore happened Error:",e
                time.sleep(2)
        else:
            time.sleep(2)
            print i,"--clickShowMore-not enabled---",element                 
    time.sleep(5)


def eastMoneyWebScrapy(filePath):
    securityID_name_dict = eastMoneySecurityictWebScrapy()
    filenew = open(filePath,"w")
    browers = webdriver.Chrome()
    url = r"http://gubatopic.eastmoney.com/"
    now = datetime.datetime.now()
    nowtime = now.strftime('%Y%m%d%H%M%S')
    nowtime = nowtime+"000"
    date = time.strftime('%Y%m%d',time.localtime(time.time()))
    print  nowtime
    print url    
    try:
        browers.get(url)
        for i in range(2):
            clickShowMore(browers)
            clickLoadMore(browers)
            clickShowMore(browers)
                
        topicList = browers.find_elements_by_xpath("//li[@class='clearfix']")
    #     discussList = browers.find_elements_by_xpath("//div[@class='hotTopicMsg fr']/p[@class='f12']")
    #     securityIDList = browers.find_elements_by_xpath("//div[@class='indexStockLink f12']/div[@class='indexStockList']")
    #     securityNameList = browers.find_elements_by_xpath("//div[@class='indexStockLink f12']/ul[@class='indexStockList']/a@title")
    #     securityID = browers.find_elements_by_xpath("//li[@class='clearfix']//a")
    #     print securityID
        topic_i = 0
        for topic_i in xrange(len(topicList)):
            print str(topicList[topic_i].text)
            comment =  str(topicList[topic_i].text).split("\n")
            for comment_i in xrange(len(comment)):            
                line = comment[comment_i]
                line = line.lstrip()
                line = line.rstrip()
                line1 = re.search("#",line)
                line2 = re.search("讨论数", line) 
                line3 = re.search("%|-", line)
                             
                if line1 is not None:
                    hotTopic = re.sub("#","",line)
                if line2 is not None:
                    lines2 = line.split("：")
                    discussionNumbers = lines2[1].split()[0]
                    tenThousandIs = re.search("\xe4", discussionNumbers)
                    if tenThousandIs is not None:
                        discussionNumbers = int(float(discussionNumbers.split("\xe4")[0])*10000)
                    broswingNumbers = str(lines2[2].split("\xe4")[0])          
                if line3 is not None:
                    lines = line.split()
                    for lines_i in lines:
                        linere2 = re.search("\w|-", lines_i)
                        if linere2 is not None:
                            continue
                        else:
                            if hotTopic is not None:
                                filenew.write(date)
                                filenew.write('\t')                                
                                filenew.write(nowtime)
                                filenew.write('\t')
                                filenew.write(hotTopic)
                                filenew.write('\t')
                                filenew.write(str(discussionNumbers))
                                filenew.write('\t')
                                filenew.write(broswingNumbers)
                                filenew.write('\t')
                                if securityID_name_dict.has_key(lines_i):                           
                                    filenew.write(securityID_name_dict[lines_i])
                                    filenew.write('\t')
                                else:
                                    filenew.write("null")
                                    filenew.write('\t')
                                filenew.write(lines_i)                               
                                filenew.write('\n')
                    hotTopic = None
                    discussionNumbers = 0
                    broswingNumbers = 0
        filenew.close()        
    except Exception,e:
        print e

def eastMoneyWebScrapyToFile():        
        date = time.strftime('%Y%m%d',time.localtime(time.time()))
        filePath = "D:\\ZYP\\hottopic"+date+".txt"
        eastMoneyWebScrapy(filePath)
        
def fileToMysql():
    date = time.strftime('%Y%m%d',time.localtime(time.time()))
    filePath = "D:\\ZYP\\hottopic"+date+".txt"
    file_to_read = open(filePath,'r')
    line = file_to_read.readline()
    dataline = [];
    hottopic = [];
    while line:
        line = line.lstrip()
        line = line.rstrip()
        dataline = line.split("\t")
        hottopic.append(dataline)
    
    config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '111111',
    'db': 'hangqing_his',
    'charset': 'utf8'
    }
    conn = mdb.connect(**config)
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO t_md_hot_topic values(%s,%d,%s,%s,%s,%s,%s)',hottopic[0])
        conn.commit()
    except:
        import traceback
        traceback.print_exc()
        # 发生错误时会滚
        conn.rollback()
    finally:
        
        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        conn.close()

   
   
    
if __name__ == '__main__':
#     eastMoneyWebScrapyToFile()
    fileToMysql()

