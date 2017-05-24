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

class supercuts(scrapy.Spider):
	name = 'supercuts'
	domain = 'https://www.supercuts.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.supercuts.com/salon-directory.html'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="content parsys"]//a/@href').extract()
		for state in state_list : 
			yield scrapy.Request(url=state, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="salon-group col-md-10 col-xs-12"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@class="salonlrgtxt"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]//a/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//div[contains(@class, "store-hours")]/span')
			for hour in hour_list:
				temp = self.eliminate_space(hour.xpath('.//text()').extract())
				for te in temp:
					h_temp += te.strip() + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			if item['country'] != 'Canada':
				yield item		

		except:
			pass

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
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
			return item.strip().replace('\r','').replace('\n','').replace('\t','')
		except:
			return ''