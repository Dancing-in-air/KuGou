# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import os


class KugouPipeline(object):
    def process_item(self, item, spider):
        print(item)
        file_path = '/home/tarena/music/'+item["title_rank"]
        song_path = file_path + '/' + item["title_song"] + '.mp3'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        elif not os.path.exists(song_path):
            response = requests.get(item["url_down"])
            with open(song_path, "wb") as f:
                f.write(response.content)
        else:
            print("歌曲已经存在")
