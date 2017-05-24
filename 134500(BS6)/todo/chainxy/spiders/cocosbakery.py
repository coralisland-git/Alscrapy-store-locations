import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import unicodedata

class cocosbakery(scrapy.Spider):
	name = 'cocosbakery'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.cocosbakery.com/wp-admin/admin-ajax.php?action=store_search&lat=36.778261&lng=-119.41793239999998&max_results=500&radius=500&autoload=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['store'])
			item['store_number'] = self.validate(store['id'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = self.validate(store['country'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			h_temp = ''
			hour_list = etree.HTML(self.validate(store['description'])).xpath('.//text()')
			tmp = []
			for hour in hour_list:
				if hour.strip() != '':
					tmp.append(hour.strip())
			hour_list = tmp
			item['phone_number'] = hour_list[0]
			for cnt in range(1, len(hour_list)-1):
				h_temp += self.validate(hour_list[cnt]) +' '
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(';','')
		except:
			return ''