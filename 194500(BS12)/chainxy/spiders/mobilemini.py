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

class mobilemini(scrapy.Spider):
	name = 'mobilemini'
	domain = 'https://www.mobilemini.com'
	history = []
	
	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.mobilemini.com/locations'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="stateList"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//ul[@class="locationListing"]//a/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@id="ctl01_PageTitle"]/text()').extract_first())
			check = response.url.split('/')[-2]
			item['country'] = self.check_country(check)
			detail = self.eliminate_space(response.xpath('//div[@class="column2 clearfix"]//div[1]//text()').extract())
			if item['country'] == 'Canada':
				item['address'] = self.format(detail[0], '')
				addr = self.format(detail[1], ',').split(',')
				item['city'] = self.validate(addr[0])
				item['state'] = self.validate(addr[1])
				item['zip_code'] = self.validate(addr[2])
			else:
				address = self.format(detail[0],' ') + ' ' + self.format(detail[1], ' ')
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
			item['phone_number'] = detail[3]
			item['store_hours'] = self.validate(self.eliminate_space(detail[4].split('Hours:'))[1])
			yield item			
		except:
			pass

	def check_country(self, item):
		if 'PR' in item.upper():
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if state['abbreviation'] in item.upper():
					return 'United States'
			return 'Canada'

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def format(self, item, unit):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', unit).strip()
		except:
			return ''