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

class asashop(scrapy.Spider):
	name = 'asashop'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://members.asashop.org/4DCGI/directory/findshopresults.html?Action=asa&asa_Activity=MemberDirectory'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//td[@class="mainarea"]//tr//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//td[@class="mainarea"]//table//td//h2/text()').extract_first())
			address = self.str_concat(response.xpath('//td[@class="mainarea"]//table//td/text()').extract(), ', ')
			item['address'] = ''
			item['city'] = ''
			item['state'] = ''
			item['zip_code'] = ''
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
			item['country'] = self.check_country(item['state'])
			if item['country'] == 'Canada':
				item['address'] = self.validate(address.split(',')[0])
				item['city'] = self.validate(address.split(',')[1])
				item['state'] = self.validate(address.split(',')[2])[:2]
				item['zip_code'] = self.validate(address.split(',')[2])[2:].strip()
			item['phone_number'] = self.validate(response.xpath('//td[@class="mainarea"]//table//td//h2//a/text()').extract_first())
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
		if len(item) > 3:
			item = self.get_state(item)
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item.upper() in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''