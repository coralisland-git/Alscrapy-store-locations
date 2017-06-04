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

class napaonline(scrapy.Spider):
	name = 'napaonline'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.napaonline.com/en/store-finder?q='+location['city']
			self.header = {
				"Accept":"text/html, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest",
				"X-Distil-Ajax":"vaxycdfb",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=self.header, method='get', callback=self.body, meta={'country':'United States'}) 
		yield scrapy.Request(url='https://www.napaonline.com/en/facility-finder?territory=DO&facilityType=ACMEC', callback=self.parse_country)

	def parse_country(self, response):
		country_list = response.xpath('//select[@id="country-type-select"]//option')
		kind_list = response.xpath('//select[@id="facility-type-select"]//option/@value').extract()
		for country in country_list[1:]:
			country_name = country.xpath('./text()').extract_first()
			country_abbreviation = country.xpath('./@value').extract_first()
			for kind in kind_list:
				url = 'https://www.napaonline.com/en/facility-finder?territory=%s&facilityType=%s' %(country_abbreviation, kind)
				yield scrapy.Request(url=url, headers=self.header, method='get', callback=self.body, meta={'country':country_name})


	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store-listing"]//li')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[@class="title-1"]/text()').extract_first()) + ' ' + self.validate(store.xpath('.//div[@class="title-2"]/text()').extract_first())
				address = self.validate(store.xpath('.//div[@class="address-1"]/text()').extract_first()) + ' ' + self.str_concat(store.xpath('.//div[@class="address-2"]/text()').extract(), ', ')
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
				item['country'] = response.meta['country']
				item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]/text()').extract_first())
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//div[@class="store-hours"]//div[@class="store-hours-block"]//text()').extract())
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
			return item.replace('\xa0', '').strip().replace('\n',' ').replace('\r','').replace('\t','')
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
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''