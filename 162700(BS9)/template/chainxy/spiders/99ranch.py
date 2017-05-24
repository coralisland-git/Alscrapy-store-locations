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

class ranch(scrapy.Spider):
	name = '99ranch'
	domain = 'https://www.99ranch.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.99ranch.com/store-locator?L=1&input=%s&distance=100' %location['city']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[contains(@class, "no-textdec")]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[@class="store-details"]')
		item = ChainItem()
		address = ''
		address_temp = self.eliminate_space(detail.xpath('.//div[contains(@class, "store-address")]//text()').extract())
		for temp in address_temp:
			if '(' in temp:
				item['phone_number'] = temp
			address += temp + ', '			
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(address)
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += temp[0].replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] = temp[0]
			elif temp[1] == 'ZipCode':
				item['zip_code'] = temp[0].replace(',','')
			else:
				item['address'] += temp[0].replace(',', '') + ' '
		item['country'] = 'United States'
		h_temp = ''
		hour_list = self.eliminate_space(detail.xpath('.//div[contains(@class, "store-time")]//text()').extract())
		for hour in hour_list:
			h_temp += self.format(hour) + ' '
		item['store_hours'] = self.validate(h_temp)
		if item['address']+item['phone_number'] not in self.history:
			self.history.append(item['address']+item['phone_number'])
			yield item			

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

	def format(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '-').replace('\u2010','-').replace('\xa0','').strip()
		except:
			return ''