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

class petdepot(scrapy.Spider):
	name = 'petdepot'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://petdepot.net/wp-admin/admin-ajax.php?action=store_search&autoload=1'
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
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			h_temp = ''
			hour_list = etree.HTML('<div>'+self.validate(store['hours'])+'</div>').xpath('//div/text()')
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			


	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
