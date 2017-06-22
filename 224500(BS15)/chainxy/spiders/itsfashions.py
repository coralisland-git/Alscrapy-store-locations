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

class itsfashions(scrapy.Spider):
	name = 'itsfashions'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.itsfashions.com/location.aspx?stores=both&state=%s' %location['abbreviation'].lower()
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="location"]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				if len(detail) == 4:
					address = detail[2] + ', ' + detail[3] 
				else:
					item['store_name'] = self.validate(detail[2])
					address = detail[3] + ', ' + detail[4] 
				item['address'] = ''
				item['city'] = ''
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
				item['country'] = 'United States'
				p_temp = store.xpath('.//text()').extract()
				item['phone_number'] = ''
				for temp in p_temp:
					if '-' in temp and len(temp.split('-')) == 3:
						item['phone_number'] = temp.strip()
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
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
			if self.validate(item) != '' and 'location' not in self.validate(item).lower() and 'direction' not in  self.validate(item).lower() and '-' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp