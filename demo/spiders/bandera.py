import requests
import scrapy
from demo.util import Util
from demo.items import DemoItem
from bs4 import BeautifulSoup as bs
from scrapy.http import Request, Response
import re
import time


class BanderaSpider(scrapy.Spider):#有很多403
    name = 'bandera'
    allowed_domains = ['bandera.inquirer.net']
    website_id = 376  # 网站的id(必填)
    language_id = 2117  # 所用语言的id
    start_urls = ['https://bandera.inquirer.net/balita',
                  'https://bandera.inquirer.net/category/opinyon',
                  'https://bandera.inquirer.net/chika',
                  'https://bandera.inquirer.net/category/lotto']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_rht',
        'password': 'dg_rht',
        'db': 'dg_test'
    }

    def __init__(self, time=None, *args, **kwargs):
        super(BanderaSpider, self).__init__(*args, **kwargs)
        self.time = time

    def parse(self, response):
        soup = bs(response.text,"html.parser")
        for i in soup.select("#lmd-headline"):
            news_url = i.find("a").get("href")
            yield scrapy.Request(news_url,callback=self.parse_news)

        url = soup.select("#lmd-headline")[-1].find("a").get("href")
        soup1 = bs(requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}).text,"html.parser")
        pub = soup1.find(id ="m-pd2").find_all("span")[-1].text
        if self.time == None or Util.format_time3(Util.format_time2(pub)) >= int(self.time):
            for a in soup.select("#landing-read-more > a"):
                if a.text == 'Next':
                    url = a.get("href")
                    yield scrapy.Request(url,callback=self.parse)
        else:
            self.logger.info('时间截止')

    def parse_news(self,response):
        item = DemoItem()
        soup = bs(response.text,"html.parser")

        item["category1"] = soup.select_one("#m-bread2 > a").text
        item["category2"] = None
        title = soup.select_one("#landing-headline > h1").text
        item["title"] = title
        pub_time = soup.select("#m-pd2 > span")[-1].text
        item["pub_time"] = Util.format_time2(pub_time)
        images = [img.find("img").get("src") for img in soup.find_all(class_="wp-caption aligncenter")] if soup.find_all(class_="wp-caption aligncenter") else []
        item["images"] = images
        abstract = soup.find(id="article-content").find("p").text.strip() if soup.find(id="article-content").find("p") else None
        item["abstract"] = abstract
        body = ''
        if soup.find(id="article-content").find_all("p"):
            for p in soup.find(id="article-content").find_all("p"):
                body += (p.text.strip() + '\n')
        item["body"] = body

        self.logger.info(item)
        yield item

