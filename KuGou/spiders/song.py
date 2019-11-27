# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from lxml import etree
from copy import deepcopy


class SongSpider(scrapy.Spider):
    name = 'song'
    allowed_domains = ['kugou.com']
    start_urls = ['https://www.kugou.com/yy/html/rank.html']
    cookies = "kg_mid=a4aea1dccb0ca4f9d730da5581c11e6e; kg_dfid=3ve36F1twpJ10Xx8Jx0hgQG8; KuGooRandom=66261573043938286; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; ACK_SERVER_10015=%7B%22list%22%3A%5B%5B%22bjlogin-user.kugou.com%22%5D%5D%7D; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1573868302,1574738143,1574749200,1574749753; kg_mid_temp=a4aea1dccb0ca4f9d730da5581c11e6e; ACK_SERVER_10016=%7B%22list%22%3A%5B%5B%22bjreg-user.kugou.com%22%5D%5D%7D; ACK_SERVER_10017=%7B%22list%22%3A%5B%5B%22bjverifycode.service.kugou.com%22%5D%5D%7D; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1574751838"
    cookies = {i.split("=")[0].strip(): i.split("=")[1].strip() for i in cookies.split(";")}

    def start_requests(self):
        """
        重构start_requests,携带cookies
        :return:
        """
        yield scrapy.Request(self.start_urls[0], callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        """
        获取首页,提取榜单名字和榜单url地址
        :param response:
        :return:
        """
        li_list = response.xpath("//div[@class='pc_rank_sidebar pc_rank_sidebar_first ']/ul/li")
        for li in li_list:
            item = dict()
            item["title_rank"] = li.xpath("./a/@title").extract_first()
            item["title_url"] = li.xpath("./a/@href").extract_first()
            yield scrapy.Request(item["title_url"], callback=self.parse_songs, meta={"item": item})

    def parse_songs(self, response):
        """
        获取榜单页,提取歌曲名字和歌曲播放地址
        :param response:
        :return:
        """
        item = response.meta["item"]
        li_songs_list = response.xpath("//div[@id='rankWrap']/div[2]/ul/li")
        for li in li_songs_list:
            item["title_song"] = li.xpath("./@title").extract_first()
            item["url_song"] = li.xpath("./a/@href").extract_first()
            # print(item)
            yield scrapy.Request(item["url_song"], callback=self.parse_song, meta={"item": deepcopy(item)})

    def parse_song(self, response):
        """
        获取歌曲下载地址
        :param response:
        :return:
        """
        item = response.meta["item"]
        url_song = response.url
        print(url_song)
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--disable-gpu")
        options.add_argument(
            'user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"')
        prefs = {"profile.default_content_setting_values": {"images": 2}}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)
        # driver.add_cookie(self.cookies)
        driver.get(url_song)
        html = driver.page_source
        # print(html)
        item["url_down"] = etree.HTML(html).xpath("//audio[@id='myAudio']/@src")
        if item["url_down"] is not None:
            item["url_down"] = etree.HTML(html).xpath("//audio[@id='myAudio']/@src")[0]
        yield item
