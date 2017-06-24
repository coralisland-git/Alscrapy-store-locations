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

class napacanada(scrapy.Spider):
	name = 'napacanada'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.napaonline.com/en/store-finder?q=' + location['city'].split('(')[0].strip() + '&page=100'
			header = {
				"Accept":"text/html, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Distil-Ajax":"vaxycdfb",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store-listing"]//ul//li')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[@class="title-2"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//div[@class="address-1"]/text()').extract_first())
				address = self.validate(store.xpath('.//div[@class="address-2"][2]/text()').extract_first())
				addr = address.split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip()[:2])
				item['zip_code'] = self.validate(addr[1].strip()[2:])
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]/text()').extract_first())
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//div[@class="store-listing-hours"]//text()').extract())
				cnt = 1
				for hour in hour_list:
					h_temp += hour
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
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