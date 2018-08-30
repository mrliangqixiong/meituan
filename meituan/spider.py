#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Define a meituan api spider class allows you to fetch meituan
restaurants infos in haikou city.
'''

import csv
import os
import time
import pymysql
import requests
import random

from meituan.settings import headers, savePath, filename, sqlConf, tableName, limit, areaid
import json


class MT_spider(object):
    baseUrl = ("http://api.meituan.com/group/v4/deal/select/city/{0}/cate/1?"
               "sort=solds&hasGroup=true&mpt_cate1=1&offset={1}&limit={2}")
    modeList = ['txt', 'csv', 'mysql']
    tableName = tableName

    # 美团深圳地区美食爬虫
    def __init__(self, saveMode='txt'):
        if saveMode not in self.modeList:
            raise RuntimeError('存储模式指定有误，请输入txt、csv或者mysql')
        self.saveMode = saveMode

        if self.saveMode == 'mysql':
            self.conn = pymysql.connect(**sqlConf)
            self.cur = self.conn.cursor()

            sql = '''CREATE TABLE IF NOT EXISTS {0}(
                id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
                shopName VARCHAR(60),
                cateName VARCHAR(30),
                # brandName VARCHAR(128),
                # brandId integer ,
                # brandLogo VARCHAR(256),
                avgScore FLOAT,
                avgPrice FLOAT ,
                lowestPrice FLOAT ,
                areaName VARCHAR(30),
                # areaId integer,
                lat FLOAT,
                lng FLOAT,
                addr VARCHAR(128),
                parkingInfo VARCHAR (256),
                abstracts TEXT,
                openInfo VARCHAR(128),
                phone VARCHAR(60),
                introduction TEXT,
                featureMenus TEXT,
                latestWeekCoupon integer ,
                historyCouponCount integer 
                # isSupportAppointment VARCHAR (30)
                );'''.format(self.tableName)
            # print(sql)
            self.cur.execute(sql)
            self.conn.commit()
        else:
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            filePath = os.path.join(savePath, filename + '.' + self.saveMode)
            if not os.access(filePath, os.F_OK):
                with open(filePath, 'w', encoding='utf-8', newline='') as file:
                    if self.saveMode == 'csv':
                        csvwriter = csv.writer(file)
                        csvwriter.writerow(
                            ['店铺名称', '类别', '评分', '所属片区', '纬度', '经度', '详细地址', '优惠套餐情况', '营业时间', '联系电话', '累计售出份数', '餐厅简介',
                             '特色菜'])
            self.file = open(filePath, 'a', encoding='utf-8', newline='')
            if self.saveMode == 'csv':
                self.csvwriter = csv.writer(self.file)

    def run(self):
        i = 0
        acquiredCount = 0
        while True:
            try:
                url = self.baseUrl.format(areaid, str(i * limit), limit)
                print('>>>> url =', url)
                itemlist = self.parse(url)
                if not itemlist:
                    break
                for item in itemlist:
                    self.save_item(item)
                acquiredCount += len(itemlist)
                print('已成功请求%d个商家信息' % ((i + 1) * limit))
                print('已成功获取%d个商家信息' % (acquiredCount))
                i += 1
                # time.sleep(random.randint(2, 5))
                time.sleep(random.randint(2, 5))
            except Exception as e:
                print(e)

    def save_item(self, item):
        if self.saveMode == 'txt':
            for k, v in item.items():
                self.file.write(str(k) + ':' + str(v) + '\n')
            self.file.write('\n\n-----------------------------\n\n\n')
        elif self.saveMode == 'csv':
            print('>> writing to csv file.')
            self.csvwriter.writerow(item.values())
        else:
            sql = '''
            INSERT INTO {0}(shopName,cateName,avgScore,avgPrice,lowestPrice,areaName,
            lat,lng,addr,parkingInfo,abstracts,openInfo,phone,introduction,
            featureMenus,latestWeekCoupon,historyCouponCount)
            VALUES ('{店铺名称}','{类别}','{评分}','{平均价格}','{最低价格}','{所属片区}',
            '{纬度}','{经度}','{详细地址}','{停车信息}','{优惠套餐情况}','{营业时间}','{联系电话}',
            '{餐厅简介}','{特色菜}','{上周订单数}','{累计售出份数}')
            '''.format(self.tableName, **item)
            # print(sql)
            self.cur.execute(sql)
            self.conn.commit()

    def parse(self, url):
        response = requests.get(url, headers=random.choice(headers))
        number = 0
        while True:
            try:
                info_dict = json.loads(response.text)
                info_list = info_dict['data']
                if info_list:
                    break
                else:
                    number += 1
                    if number >= 10:
                        return None
                    time.sleep(10)
                    response = requests.get(url, headers=random.choice(headers))
            except:
                number += 1
                if number >= 10:
                    return None
                time.sleep(10)
                response = requests.get(url, headers=random.choice(headers))

        itemlist = []
        for info in info_list:
            # 店铺名称
            name = info['poi']['name']
            # 页面id
            # poiId = info['poi']['poiid']
            # 品牌名称
            # brandName = info['poi']['brandName']
            # 品牌id
            # brandId = info['poi']['brandId']
            # 品牌logo
            # brandLogo = info['poi']['brandLogo']
            # 平均价格
            avgPrice = info['poi']['avgPrice']
            # 最低价格
            lowestPrice = info['poi']['lowestPrice']
            # 所属片区
            areaName = info['poi']['areaName']
            # 地区id
            # areaId = info['poi']['areaId']
            # 详细地址
            addr = info['poi']['addr']
            # 纬度
            lat = info['poi']['lat']
            # 经度
            lng = info['poi']['lng']
            # 餐厅类别
            cateName = info['poi']['cateName']
            # 优惠套餐情况
            abstracts = ''
            for abstract in info['poi']['payAbstracts']:
                # abstracts.append(abstract['abstract'])
                abstracts = abstracts + abstract['abstract'] + ';'

            # 评分
            avgScore = info['poi']['avgScore']
            # 楼层
            # floor = info['poi']['floor']
            # 停车信息
            parkingInfo = info['poi']['parkingInfo']
            # 营业时间
            openInfo = info['poi']['openInfo'].replace('\n', ' ')
            # 联系电话
            phone = info['poi']['phone']
            # 餐厅简介
            introduction = info['poi']['introduction']
            # 特色菜
            featureMenus = info['poi']['featureMenus']
            # 是否小吃
            # isSnack = info['poi']['isSnack']
            # 有无外卖
            # isWaimai = info['poi']['isWaimai']
            # 上周订单数
            latestWeekCoupon = info['poi']['latestWeekCoupon']
            # 历史订单数
            historyCouponCount = info['poi']['historyCouponCount']
            # wifi
            # wifi = info['poi']['wifi']
            # 支持预定
            # isSupportAppointment = info['poi']['isSupportAppointment']
            item = {
                '店铺名称': name,
                # '页面id': poiId,
                '类别': cateName,
                '评分': avgScore,
                # '品牌名称': brandName,
                # '品牌id': brandId,
                # '品牌logo': brandLogo,
                '平均价格': avgPrice,
                '最低价格': lowestPrice,
                '所属片区': areaName,
                # '地区Id': areaId,
                '纬度': lat,
                '经度': lng,
                '详细地址': addr,
                # '楼层': floor,
                '停车信息': parkingInfo,
                '优惠套餐情况': abstracts,
                '营业时间': openInfo,
                '联系电话': phone,
                '餐厅简介': introduction,
                '特色菜': featureMenus,
                # '是否小吃': isSnack,
                # '有无外卖': isWaimai,
                # '上周订单数': latestWeekCoupon,
                '累计售出份数': historyCouponCount,
                # 'wifi': wifi,
                # '支持预定': isSupportAppointment
            }

            itemlist.append(item)
        # 返回当前页面item列表
        return itemlist

    def __del__(self):
        if self.saveMode == 'mysql':
            self.cur.close()
            self.conn.close()
        else:
            self.file.close()


# test:
if __name__ == '__main__':
    spider = MT_spider(saveMode='mysql')
    spider.run()
