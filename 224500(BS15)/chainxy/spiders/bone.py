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

class bone(scrapy.Spider):
	name = 'bone'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.rag-bone.com/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="sl__store-details"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//a[@class="sl__store-details-name"]/text()').extract_first())				
				address = self.str_concat(self.eliminate_space(store.xpath('.//div[contains(@class, "sl__store-details-adress")]//text()').extract())[1:-2], ', ')
				item['address'] = ''
				item['city'] = ''
				item['state'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				if item['state'] != '':
					item['country'] = self.check_country(item['state'])
					item['phone_number'] = store.xpath('.//div[contains(@class, "sl__store-details-adress")]//a[1]/text()').extract_first()
					item['latitude'] = self.validate(store.xpath('./@data-pin').extract_first()).split('",')[1].split(',')[0]
					item['longitude'] = self.validate(store.xpath('./@data-pin').extract_first()).split('",')[1].split(',')[1]
					h_temp = ''
					hour_list = self.eliminate_space(store.xpath('.//div[contains(@class, "sl__store-details-hours")]//text()').extract())
					for hour in hour_list:
						if '-' in hour:
							h_temp += self.validate(hour) + ', '
					item['store_hours'] = h_temp[:-2]
					if item['country'] == 'US':
						yield item	
			except:
				pass	

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\t','').replace('\r','')
		except:
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

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''