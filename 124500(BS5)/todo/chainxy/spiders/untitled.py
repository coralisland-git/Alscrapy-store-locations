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
import pdb

class cookout(scrapy.Spider):
	name = 'cookout'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'http://www.cookout.com/wp-admin/admin-ajax.php?action=store_search&lat=36.072635&lng=-79.79197499999998&max_results=500&radius=500&autoload=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = 'Cook Out'
			item['store_number'] = store['id']
			item['address'] = store['address']
			item['address2'] = store['address2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip']
			item['country'] = store['country']
			item['phone_number'] = store['phone']
			h_temp = ''
			hour_list = etree.HTML(store['hours']).xpath('//table//tr')
			for hour in hour_list:
				try:
					h_temp += self.validate(hour.xpath('.//td[1]/text()')[0]) + ' ' + self.validate(hour.xpath('.//td[2]//text()')[0]) + ', '
				except:
					pdb.set_trace()
			item['store_hours'] = h_temp[:-2]
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''