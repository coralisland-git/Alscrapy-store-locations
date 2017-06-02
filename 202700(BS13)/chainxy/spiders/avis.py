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

class avis(scrapy.Spider):
	name = 'avis'
	domain = 'https://www.avis.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'https://www.avis.com/en/locations/avisworldwide'
		yield scrapy.Request(url=init_url, callback=self.parse_country) 

	def parse_country(self, response):
		country_list = response.xpath('//div[@class="wl-location-state"]//a/@href').extract()
		for country in country_list:
			country_link = self.domain + country
			yield scrapy.Request(url=country_link, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="country-wrapper row"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_city)	

	def parse_city(self, response):
		city_list = response.xpath('//a[@class="location-heading"]/@href').extract()
		if city_list:
			for city in city_list :
				city_link = self.domain + city
				yield scrapy.Request(url=city_link, callback=self.parse_store)
		else:
			yield scrapy.Request(url=response.url, callback=self.parse_store, dont_filter=True)
	
	def parse_store(self, response):
		store_list = response.xpath('//li[@class="loopFour clearfix"]//a/@href').extract()
		for cnt in range(0, len(store_list)/2, 2):
			if cnt % 2 == 0:
				store_link = self.domain + store_list[cnt]
				yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="location-page-g"]//span[@itemprop="name"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())[:-1].strip()
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())[:-1].strip()
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())[:-1].strip()
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())[:-1].strip()
			item['country'] = self.validate(response.xpath('//span[@itemprop="addressCountry"]/text()').extract_first())
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
			return item.strip().replace(';',', ')
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