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
import pdb

class todo1(scrapy.Spider):
	name = 'todo1'
	domain = 'https://locations.cititrends.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'https://locations.cititrends.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			if len(state.split('/')) == 1:
				yield scrapy.Request(url=state_link, callback=self.parse_city)	
			elif len(state.split('/')) == 2:				
				yield scrapy.Request(url=state_link, callback=self.parse_store)
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_page)

	def parse_city(self, response):
		city_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			if len(city.split('/')) == 2:
				yield scrapy.Request(url=city_link, callback=self.parse_store)
			else:
				yield scrapy.Request(url=city_link, callback=self.parse_page)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="c-location-grid-item"]//h5//a/@href').extract()
		for store in store_list:
			store_link = self.domain + store[3:]
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@itemprop="name"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = self.validate(response.xpath('//abbr[@itemprop="addressCountry"]/text()').extract_first())
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			item['latitude'] = self.validate(response.xpath('//meta[@itemprop="latitude"]/@content').extract_first())
			item['longitude'] = self.validate(response.xpath('//meta[@itemprop="longitude"]/@content').extract_first())
			item['store_hours'] = self.validate(response.xpath('//span[@itemprop="openingHours"]/text()').extract_first())
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