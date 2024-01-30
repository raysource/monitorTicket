#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Project: 某网回流票监控
import json
import random
import sys
import hashlib as hash
from selenium import webdriver
from curl_cffi import requests
import schedule
from selenium.webdriver.common.by import By
import requests as nreq
import threading


class Monitor(object):
    # 构造请求头等
    def __init__(self):
        # 请求url获取响应
        self.useProxy=False
        print('-----------------init__ MonitorItem-----------------')



    def get(self,browser,item_id):
        url="https://m.damai.cn/shows/item.html?itemId="+ str(item_id)+"&spm=a2o71.search.list.ditem_0"
        # 打开网页，获取 Cookie
        print("-----------------开始回流票监测:" + item_id + "---------------------------------")
        browser.get(url)
        cookies =browser.get_cookies()
        dataItem = '{"itemId":' + str(
            item_id) + ',"platform": "8", "comboChannel": "2", "dmChannel": "damai@damaih5_h5"}'
        # 输出 Cookie
        m_h5_tk = ''
        m_h5_tk_enc = ''
        cna = ''

        for cookie in cookies:
            if cookie['name'] == "_m_h5_tk":
                m_h5_tk = cookie['value']
            if cookie['name'] == "_m_h5_tk_enc":
                m_h5_tk_enc = cookie['value']
            if cookie['name'] == "cna":
                cna = cookie['value']

        print('-----------------cookie is '+m_h5_tk+'-------------------')
        if len(m_h5_tk) < 2:
            return
        token = str(m_h5_tk).split('_')[0]
        timestamp = str(m_h5_tk).split('_')[1]

        # 生成加密签名
        signString = token + '&' + timestamp + '&12574478&' + str(dataItem).replace(' ', '')
        hl = hash.md5()
        hl.update(signString.encode('UTF-8'))
        sign = hl.hexdigest().lower()

        # 设置请求头信息
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Cookie': 'isg=BPz8Ce_4td5wtoCsTXzkHCbAz5yu9aAf8Jc8gtZ9GufLoZwr_gaGr3OQgUnZ8th3;' \
                      + 'l=fB_rKNJPPxCYHcC_BOfanurza77OSIdYYuPzaNbMi9fPOE1p5aPRW1ev5-T9C31VFs12R3ShcG42BeYBcbh-nxv951xKbckmndLHR35..;' \
                      + 'tfstk=de5WQtwwAMCVri9U37aVcony9iO3uMNwP2TdSwhrJQd-vDQ906zlz8VChMI22M_3reKdvMtFULNNraAH9l5Q_57koMOLb9TFdm7ktBEab5PNrajNpZFGU2gSBuFckrGjMfuygO9a80i5GUKHXgtXoEfXPLtTsn6a5c-s0qMIldcplY4blvDnaea1s;' \
                      + 'xlly_s=1; _m_h5_tk=' + str(
                m_h5_tk) + '; _m_h5_tk_enc=' + m_h5_tk_enc + '; _samesite_flag_=true;' \
                      + '_tb_token_=54830b31d1b35; cookie2=15c7f3a10820cd5d760bea3ba9943db6;' \
                      + 't=4cfaa16de70922adabefc1e8db721afe; cna=' + cna + '; damai.cn_nickName=%E5%92%B8%E5%B8%A6%E9%B1%BC2022',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'mtop.damai.cn',
            'Origin': 'https://m.damai.cn',
            'Referer': 'https://m.damai.cn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        urlItem = "https://mtop.damai.cn/h5/mtop.alibaba.damai.detail.getdetail/1.2/?jsv=2.7.2&appKey=12574478&t=" \
              + str(m_h5_tk).split('_')[1] + "&sign=" \
              + str(sign) \
              + "&api=mtop.alibaba.damai.detail.getdetail&v=1.2&H5Request=true&type=originaljson&timeout=10000" \
              + "&dataType=json&valueType=original&forceAntiCreep=true&AntiCreep=true&useH5=true&data=%7B%22itemId%22%3A" \
              + str(
            item_id) + "%2C%22platform%22%3A%228%22%2C%22comboChannel%22%3A%222%22%2C%22dmChannel%22%3A%22damai%40damaih5_h5%22%7D"

        try:
            hrefQp = '//*[@id="bottom"]/div[2]/div[1]/div[1]/div/div/div/p[1]'
            nodeQp = browser.find_element(By.XPATH, hrefQp)
            if nodeQp != None:
                timeQp = browser.find_element(By.XPATH, '//*[@id="bottom"]/div[1]/div/div/div[2]/div[1]')

        except:
              pass
        hrefPath='//*[@id="bottom"]/div[2]/div[1]/div[1]/div/div'
        hrefNode=browser.find_element(By.XPATH, hrefPath)
        if hrefNode!=None:
            try:
                hrefNode.click()
            except:
               browser.quit()
               return

        else:
            print('取不到弹出按钮')
            browser.quit()
            return

        response =requests.get(urlItem, headers=headers, impersonate="chrome101")
        return response.json()


    def parse(self,browser,item_id,performName,skuName):
        # 将字符串数据转换成字典数据
        res = self.get(browser,item_id=item_id)
        if res == None:
            print('---------------暂时获取不到数据--------------')
            return
        resHave = res['data'].get('result')
        if resHave != None:
            resDetail = res['data']['result']

        else:
            print('---------------暂时获取不到数据--------------')
            return
        r = json.loads(resDetail)
        itemBase = r['detailViewComponentMap']['item']['staticData']['itemBase']
        itemName=itemBase['itemName']

        performBase = r['detailViewComponentMap']['item']['item']['performBases']
        performBaseLen = len(performBase)


        msgPerform=''
        msgPerformReady=''
        for i in range(0, performBaseLen):
            performs = performBase[i]['performs']

            performNameItem = performBase[i]['name']
            performBaseTagValue= performBase[i]['performBaseTagValue']
            if performBaseTagValue=='1':
                print(item_id + ":演出" +itemName+"------场次---"+ performNameItem + "------无票")
                return
            else:
                itemUrl = 'dd<a href="https://m.damai.cn/shows/item.html?itemId='\
                          + str(item_id) + '&spm = a2o71.search.list.ditem_0">' \
                          + str(item_id) + "</a>"
                msgPerformReady += itemUrl + ":演出" + itemName + "------场次---" + performNameItem + "------有票</br>"
                msgPerform=msgPerformReady
                   #return

            performLen = len(performs)
            if performLen > 0:
                for j in range(0, performLen):
                    itemId = performs[j]['itemId']
                    performNameSku = performs[j]['performName']
                    noSku=0
                    if performBaseTagValue==1:
                       noSku = performs[j]['performTagValue']
                    if noSku=='1':
                        print(item_id + ":演出" +itemName+"------场次-------"+ performNameSku + "------无票")
                    else:
                        itemUrl='aaa<a href="https://m.damai.cn/shows/item.html?itemId='\
                               + str(item_id)+'&spm = a2o71.search.list.ditem_0">'\
                               +item_id+"</a>"
                        msgPerformReady+=itemUrl + ":演出" +itemName+"------场次-------"+ performNameSku + "------有票<br/>"
                        if performName == '':
                            if msgPerform=='':
                                msgPerform + msgPerformReady
                            else:
                                msgPerform=msgPerform+'<br/>'+msgPerformReady

                        else:
                            if performName == performNameSku:
                                if msgPerform=='':
                                    msgPerform= msgPerformReady
                                else:
                                    msgPerform=msgPerform+'<br/>'+msgPerformReady


                    #print(msgPerform)
                    if performName!="":
                       if performName!=performName:
                          return
                    skuHave = performs[j].get('skuList')
                    skuNum=0
                    msg=""
                    if skuHave!=None:
                        skuList = performs[j]['skuList']

                        skuLen = len(skuList)
                        if skuLen > 0:

                           for k in range(0, skuLen):
                               # 票状态 0 有票 1缺货
                               skuTagType = skuList[k]['skuTagType']
                               # true 可售 false不可售 缺票 "quantitySellAble
                               skuEnable = skuList[k]['skuEnable']
                               quantitySellAble = skuList[k]['quantitySellAble']

                               sEnable = 1
                               if skuEnable == "false":
                                  sEnable = 0
                               if skuName!="":
                                 if skuList[k]['skuName']==skuName:
                                    if sEnable ==1:
                                       skuNum=1
                               else:
                                    if sEnable==1:
                                       skuNum=skuNum+1
                    if skuNum>0:
                        msg = item_id + ":演出" + itemName + "-场次-" + performName + " 有" + str(skuNum) + "个票档有票" + "<br/>"

                    if msgPerform!="":
                      if msg!="":
                         self.sendMsg(msg)
                      else:
                         self.sendMsg(msgPerform)

        print("-----------------结束本轮监测:" + item_id + "---------------------------------")

    # 保存为CSV数据
    def save(self):
      print("")


    def sendMsg(self,msg):

        filepath = 'push_list.txt'
        tokenArray = None
        with open(filepath, 'r', encoding="utf-8") as f:
            tokenArray = json.load(f)
            print(tokenArray)
        for n in range(0, len(tokenArray['data'])):
            token=tokenArray['data'][n]['token']
            title = '监控s通知'
            content = msg
            template = 'html'
            url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
            nreq.get(url=url)

def runJob(monitor,browser,item_id,performName='',skuName=''):
    monitor.parse(browser=browser, item_id=item_id, performName=performName, skuName=skuName)

def runThread(monitor,browser):
    filepath = 'monitor_list.txt'

    objList=None
    with open(filepath, 'r',encoding="utf-8") as f:
        objList =json.load(f)
    if objList==None:
        return

    threads=[]
    for n in range(0,len(objList['data'])):
        item=objList['data'][n]
        itemID=item['itemID']
        performName=item['performName']
        skuName=item['skuName']
        t = threading.Thread(target=runJob(monitor=monitor,browser=browser,item_id=itemID,performName=performName,skuName=skuName))
        t.start()
        threads.append(t)

    # Wait all threads to finish.
    for t in threads:
        t.join()

    print('-----------------Main thread has ended!-----------------')
    sys.exit(0)



if __name__ == '__main__':

    print('-----------------begin Run monitorItem.py---------------')
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--window-size = 800x600')
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--remote-allow-origins=*")

    monitor=Monitor()
    browser = webdriver.Chrome(options=options)


    schedule.every(6).seconds.do(runThread, monitor,browser)
    while True:
        schedule.run_pending()


