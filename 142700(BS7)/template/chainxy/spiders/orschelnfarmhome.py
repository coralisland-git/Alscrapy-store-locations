import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class orschelnfarmhome(scrapy.Spider):
    name = 'orschelnfarmhome'
    domain = 'https://www.orschelnfarmhome.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.orschelnfarmhome.com/view/page/stores'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        data = response.body.split('data.mixin({},')[1].split(');};;')[0].strip()
        valid_data = self.validate(data)
        store_list = json.loads(data)
        for store in store_list:
            item = ChainItem()
            item['store_name'] = store_list[store]['sku_name'].split('#')[0].strip()
            item['store_number'] = store
            item['address'] = store_list[store]['address']
            item['state'] = store_list[store]['state']
            item['city'] = store_list[store]['city']
            item['zip_code'] = store_list[store]['zipcode']
            item['country'] = store_list[store]['country']
            item['latitude'] = store_list[store]['latitude']
            item['longitude'] = store_list[store]['longitude']
            item['phone_number'] = store_list[store]['phone']
            item['store_hours'] = store_list[store]['hours']
            yield item

    def validate(self, item):
        try:
            return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
        except:
            return ''


