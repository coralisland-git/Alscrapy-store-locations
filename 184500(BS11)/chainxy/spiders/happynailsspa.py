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
import usaddress

class happynailsspa(scrapy.Spider):
	name = 'happynailsspa'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.happynails.com/wp-admin/admin-ajax.php?action=store_search&lat=33.717471&lng=-117.831143&max_results=100&radius=1000'		
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['store'])
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['zip'])
				item['country'] = self.validate(store['country'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				h_temp = ''
				hour_list = self.eliminate_space(etree.HTML(self.validate(store['hours'])).xpath('//table//tr//text()'))
				cnt = 1
				for hour in hour_list:
					h_temp += hour
					if cnt % 2 == 0:
						h_temp += ', '
					else :
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('&#038;', '')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp