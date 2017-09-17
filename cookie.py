#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/13 10:59
# @Author  : Gary
# @Site    : 
# @File    : cookie.py
# @Software: PyCharm
from selenium import webdriver
from collections import defaultdict
import pickle
import os
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from PIL import Image
import js2xml
from parsel import Selector
from MyQR import myqr

from operator import itemgetter





def login():
    qrurl = getqrurl(driver.page_source)
    print(qrurl)
    showImg(qrurl)
    try:
        QR_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="J-loginMethod-tabs"]/li[1]'))
            , u'等待扫码登录'
        )
        QR_element.click()
        
        print('Wait for scan QR code...')
        
        portal_page = WebDriverWait(driver, 100).until(
            EC.url_contains('my.alipay.com/portal'), u'登录成功'
        )
        print('Successfully logged in...')
        return True
    finally:
        pass


def save_ant_flower():
    available = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="J-assets-pcredit"]/div/div/div[2]/div/p[1]/span/strong'))
    )
    total = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="J-assets-pcredit"]/div/div/div[2]/div/p[2]/strong'))
    )
    
    ant_flower = defaultdict()
    ant_flower['available'] = available.text or 0
    ant_flower['total'] = total.text or 0
    return ant_flower['total']
        # print(ant_flower)
        # with open('ant_flower.pk', 'wb') as f:
        #     pickle.dump(ant_flower, f)


def save_bills(tradeType):
    driver.get('https://consumeprod.alipay.com/record/advanced.htm')
    # 假如是标准版的话，则切换到高级版
    try:
        driver.find_element_by_link_text('切换到高级版').click()
    except:
        pass
    # 获取最近三个月&线下交易的
    js = """
    document.getElementById('J-select-range').value = 'threeMonths'
    document.getElementsByName('tradeType')[0].value = '{}'
    """.format(tradeType)
    # 获取最近一年且交易列别为指定的
    # js = """
    # document.getElementById('J-select-range').value = 'customDate'
    # document.getElementById("beginDate").value = '2016.09.16'
    # document.getElementById("endDate").value = '2017.09.16'
    # document.getElementsByName('tradeType')[0].value = '{}'
    # """.format(tradeType)
    driver.execute_script(js)
    driver.find_element_by_id("J-set-query-form").click()
    return driver.page_source


def hasNextPage():
    '检查是否有下一页，有的话则返回源代码'
    try:
        driver.find_element_by_link_text("下一页").click()
        page = driver.page_source
        return page
    except:
        print('最后一页了')
        return False


def extract_info(pagesource, tradeType):
    '根据网页源代码解析出需要的信息'
    print('*' * 10)
    print(tradeType)
    print(driver.current_url)
    sel = Selector(text=pagesource)
    for i in sel.xpath('//table/tbody/tr'):
        if len(i.xpath('td')) == 9:
            date_time = datetime.strptime(
                i.xpath('string(td[@class="time"])').extract_first().replace('\n', '').replace('\t', '')[:10],
                '%Y.%m.%d')
            name = i.xpath('td[@class="name"]/p/a/text()').extract_first()
            tradeNo = i.xpath('td[@class="tradeNo ft-gray"]/p/text()').extract_first()
            out_name = i.xpath('td[@class="other"]/p/text()').extract_first().strip()
            amount = i.xpath('td[@class="amount"]/span/text()').extract_first()
            status = i.xpath('td[@class="status"]/p/text()').extract_first()
            infolist.append({
                'datetime': date_time, 'status': status, 'tradeType': tradeType,
                'name': name, 'tradeNo': tradeNo, 'out_name': out_name, 'amount': amount,
                
            })


def getqrurl(page_source):
    '返回二维码的url'
    sel = Selector(text=page_source)
    jscode = sel.xpath('//script[contains(.,"light.page.scProducts.push(barcode)")]/text()').extract_first()
    parsed_js = js2xml.parse(jscode)
    return parsed_js.xpath('//property[@name="barcode"]/string/text()')[0]


def run(pagesource, tradeType):
    extract_info(pagesource, tradeType)
    while True:
        nextpagesource = hasNextPage()
        if nextpagesource:
            extract_info(nextpagesource, tradeType)
        else:
            break


def showImg(url):
    version, level, qr_name = myqr.run(
        url,
        version=1,
        level='H',
        picture=None,
        colorized=False,
        contrast=1.0,
        brightness=1.0,
        save_name='qrcode.jpg',
        save_dir=os.getcwd()
    )
    im = Image.open('qrcode.jpg')
    im.show()


def pachong():
    global infolist
    global driver
    infolist = []
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")  # 设置user-agent请求头
    dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
    # driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver = webdriver.Chrome(desired_capabilities=dcap)
    
    driver.get('https://auth.alipay.com/login/index.htm')
    

    options = webdriver.ChromeOptions()
    tradeType = [
        # "SHOPPING"
        "SHOPPING", "OFFLINENETSHOPPING", "FINANCE",
        "TRANSFER", "CCR", "PUC_CHARGE", "DEPOSIT",
        "WITHDRAW", "PERLOAN",
        "MOBILE_RECHARGE"
    ]
    if login():
        flower_total = save_ant_flower()
        
        for i in tradeType:
            pagesource = save_bills(i)
            run(pagesource, i)
        driver.close()
        
        infolist = sorted(infolist, key=itemgetter('datetime'), reverse=False)
        with open('data1.pickle', 'wb') as f:
            pickle.dump((infolist,flower_total), f)
        return infolist,flower_total

    
    else:
        pass


if __name__ == '__main__':
    pachong()
