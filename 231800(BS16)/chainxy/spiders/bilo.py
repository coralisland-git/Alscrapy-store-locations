# from __future__ import unicode_literals
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
import pdb

class bilo(scrapy.Spider):
	name = 'bilo'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.bi-lo.com/Locator?search=' + location['city'] + ', ' + self.get_state(location['state'])
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, br"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="divStoresReturned"]')
		for store in store_list:
			detail = self.eliminate_space(store.xpath('.//text()').extract())
			try:
				item = ChainItem()
				item['store_number'] = detail[1]
				item['address'] = detail[2]
				addr = detail[3].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				item['country'] = 'United States'
				item['phone_number'] = ''
				for de in detail:
					if 'main phone:' in de.lower():
						item['phone_number'] = de.split('phone:')[1].strip()
					if 'hours' in de.lower():
						item['store_hours'] = de.split('today:')[1].strip().replace('to','-')
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\r','').replace('\n',' ').replace('\xa0','').replace('#','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def get_state(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['name'].lower() and item != '':
				return state['abbreviation']
		return ''