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
import unicodedata

class tagheuer(scrapy.Spider):
	name = 'tagheuer'
	domain = 'https://store.tagheuer.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_Cities_list = json.load(data_file)

	def start_requests(self):
		for location in self.US_Cities_list:
			city = 'https://store.tagheuer.com/search?query=' + location['city'].replace(' ', '+')
			yield scrapy.Request(url=city, callback=self.body)

	def body(self, response):
		store_list = response.xpath('//div[@class="components-outlet-item-search-result-basic"]/@data-lf-url').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_detail)

	def parse_detail(self, response):
		try:
			temp_list = self.eliminate_space(response.xpath('//script[@type="application/ld+json"]').extract())[1].replace('\n', '')
			temp_list = json.loads(self.validate(temp_list.replace('<script data-lf-jsonld-outlet type="application/ld+json">', '').replace('</script>', '')))
			item = ChainItem()
			item['store_name'] = self.format(temp_list['name'])
			item['store_number'] = self.validate(temp_list['url'].split('-')[0][1:])
			addr_list = self.eliminate_space(response.xpath('//address//div[@class="components-outlet-item-address-basic__line"]')[0].xpath('./text()').extract())
			item['address'] = ''
			for addr in addr_list:
				item['address'] += self.format(addr) + ' '
			item['city'] = self.validate(temp_list['address']['addressLocality'])
			if ',' in item['city']:
				item['city'] = item['city'].split(',')[0]
			state = self.validate(response.xpath('//ol[@class="breadcrumb components-navigation-breadcrumb-responsive__list"]//li')[2].xpath('./a/@data-lf-tracking').extract_first())
			item['state'] = self.format(json.loads(state)['label'])
			item['zip_code'] = self.validate(temp_list['address']['postalCode']).replace('&amp;amp;amp;amp;amp;#x27;', '')
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = self.validate(temp_list['telephone'])
			item['latitude'] = self.validate(temp_list['geo']['latitude'])
			item['longitude'] = self.validate(temp_list['geo']['longitude'])
			item['store_hours'] = self.validate(temp_list['openingHours'])
			if not item['store_number'] in self.history and item['country'] == 'United States':
				self.history.append(item['store_number'])
				yield item
		except:
			pass

	def check_country(self, item):
		if 'Puert Rico' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['name']:
					return 'United States'
			return 'Canada'

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

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
