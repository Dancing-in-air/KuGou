# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from KuGou import settings
import random
import requests


class KugouDownloaderMiddleware(object):
    PROXY_POOL_URL = 'http://localhost:5000/get'

    def get_proxy(self):
        try:
            response = requests.get(self.PROXY_POOL_URL)
            if response.status_code == 200:
                print(response.text)
                return response.text
        except ConnectionError:
            return None

    def process_request(self, request, spider):
        user_agents = settings.USER_AGENTS
        user_agent = random.choice(user_agents)
        request.headers["User-Agent"] = user_agent
        request.meta["proxy"] = self.get_proxy()
        return None
