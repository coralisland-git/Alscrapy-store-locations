from __future__ import unicode_literals
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

class splendid(scrapy.Spider):
	name = 'splendid'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.splendid.com/store-list'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "templated-item")]//div[@class="container"]//div[@class="col-sm-12"]//div[@class="row"]//div[contains(@class, "col-sm-")]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['store_name'] = detail[0]
				item['address'] = detail[1]
				addr = detail[2].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(detail[3])
				h_temp = ''
				for de in detail:
					if '-' in de:
						h_temp += de + ', '
				item['store_hours'] = h_temp[:-2]
				if item['country'] == 'US':
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''