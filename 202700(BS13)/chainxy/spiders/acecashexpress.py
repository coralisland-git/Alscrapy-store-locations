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

class acecashexpress(scrapy.Spider):
	name = 'acecashexpress'
	domain = 'https://www.acecashexpress.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'https://www.acecashexpress.com/locations'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//ul[@class="states"]//li//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_city)	

	def parse_city(self, response):
		city_list = response.xpath('//ul[@class="cities-list"]//li//a/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			yield scrapy.Request(url=city_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//ul[@class="stores no-bullet"]//p[@class="location"]//a/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.str_concat(self.validate(response.xpath('//p[@itemprop="address"]//span[@itemprop="name"]/text()').extract_first()).split(' ')[:-1], ' ')
			item['store_number'] = self.validate(response.xpath('//p[@itemprop="address"]//span[@itemprop="name"]/text()').extract_first()).split(' ')[-1]
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//abbr[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//a[@itemprop="telephone"]/text()').extract_first())
			item['latitude'] = self.validate(response.xpath('//div[@class="row module store-information"]/@data-latitude').extract_first())
			item['longitude'] = self.validate(response.xpath('//div[@class="row module store-information"]/@data-longitude').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//ul[@class="hours no-bullet"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''