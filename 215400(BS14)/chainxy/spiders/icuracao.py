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
import usaddress

class icuracao(scrapy.Spider):
	name = 'icuracao'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.oxfordlearning.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = self.format(response.body).split('var olc_elements = ')[1].split('var olc_in_page_data = ')[0].strip()[:-1]
		store_list = json.loads(data)['locationData']
		for key, store in store_list.items():
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(key)
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['prov'])
				item['zip_code'] = self.validate(store['postal'])
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['latitude'])
				item['longitude'] = self.validate(store['longitude'])
				url = self.validate(store['url'])
				if item['country'] == 'CA':
					yield scrapy.Request(url=url, callback=self.parse_page, meta={'item':item})
			except:
				pass	

	def parse_page(self, response):
		try:
			item = response.meta['item']
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="dl-item clearfix"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item
		except:
			pass


	def validate(self, item):
		try:
			return item.strip().replace('&#8211;','').replace(';','')
		except:
			return ''

	def format(self, item):
		try:
			return item.decode('UTF-8').strip()
		except:
			return ''

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item in state['name']:
				return state['country']
		return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp