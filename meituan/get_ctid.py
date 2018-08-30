import time, random
import requests
import lxml.etree
import csv

START_URL = 'http://www.meituan.com/changecity/'


class Get_CityId(object):
    lst = []
    def __init__(self):
        self.fieldnames = ['City_id', 'City_name']

        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            # 'Cookie': 'ONEAPM_BI_sessionid=4067.407|1531921501949; XSRF-TOKEN=eyJpdiI6IjQ3T3k3XC9XN2pJN3RzNWZpUnJKS2ZRPT0iLCJ2YWx1ZSI6InJjY3VsZWZEM01xZm9HbTlSRzFwblZsY0YxUlJTS3Zic0xpR3F6SnlRV1hRcE1XcFM1Y3NXTmxmWFwva0pqZkJkcUdsdk1IcG9LNWJtb1pZOUNYZlJaQT09IiwibWFjIjoiODE5YWFmMjZmNjRlZWE2OGY1YjkyOTRmYzIwYjlkNzliZjNhYmNhZmZmYmFiM2Y5Nzg0YmU5ZTg1NGE3MDZlMiJ9; lexiang_session=eyJpdiI6InpuelVPR1A2bE1Ra2s3SHlnQjVOeUE9PSIsInZhbHVlIjoiOE5CQ3dGbEtUWTNHbXFiREE4Y2lLM283VHB5WjZXakF4aHJnVlhscGhienhvNThNSHU1Z3E4eXRVb3UwcXB5U01Vd0l4QkFrM2N2SGVxMFlKODFNM2c9PSIsIm1hYyI6ImY1NzI1MzkwOGQ2NWQzZmMwZDgxYmFjZjcxMWFjZGQ0NzJlODhhMGQ2NjIzNzY1N2VlMTBlZmY0ZDM2ODU1MTEifQ%3D%3D',
            'referer': 'http://www.meituan.com/changecity/',
            # 'x - xsrf - token': 'eyJpdiI6ImFQXC8yMmhVek5WcERuc1lmaFwvaFcwZz09IiwidmFsdWUiOiJZREZYSkVIdmJMTWJOcklvM05jV2xlMlNHRlpRTWVEYmRyeFBCcm9vdEp5eGJTdmJzUkw2aFczYmROdG9QZ1VHS01WN3RrZHBsXC9WQ09OVHlBU2ZJa0E9PSIsIm1hYyI6IjM4NzI2YmYzNzM2MWNjYjBhMzQyYjBlZDJiMjU4Y2Y5NmI4MjRkMTlkN2ViMzY0YTQ2YjdjZWM1NDBkOTAwOGQifQ =='

        }

    # 获取首页数据
    def fetch(self, url):
        print(url)
        r = requests.get(url, headers=self.header)
        print(r.status_code)
        # print(r.text)
        return r.text

    # 获取城市链接地址
    def get_links(self, html):
        selector = lxml.etree.HTML(html)
        links = selector.xpath('//div[@class="city-area"]//a/@href')
        for link in links:
            link = "http:" + link
            # print(link)
            self.lst.append(link)
        return self.lst


    # 解析页面
    def parse_page(self, html):
        selector = lxml.etree.HTML(html)
        data = selector.xpath('//*[@id="main"]/script[1]/text()')[0].split("=")[2].strip().split("{")[2].split(",")
        city_id = data[0].split(":")[1]
        city_name = data[1].split(":")[1].replace('"', '')
        print(city_name, city_id)
        info = {'City_id': city_id,
                'City_name': city_name
        }
        print(info)
        try:
            with open(r'city_id.csv', 'a+', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(info)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    c = Get_CityId()
    links = c.get_links(c.fetch(START_URL))
    for link in links:
        c.parse_page(c.fetch(link))
        time.sleep(random.randint(2, 5))
