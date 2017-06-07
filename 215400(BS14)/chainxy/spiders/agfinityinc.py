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

class agfinityinc(scrapy.Spider):
	name = 'agfinityinc'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://corporate.agfinityinc.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "location-block")]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//span[@class="title name"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//address/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//address//span[@class="city"]/text()').extract_first())
				item['state'] = self.validate(store.xpath('.//address//span[@class="state"]/text()').extract_first())
				item['zip_code'] = self.validate(store.xpath('.//address//span[@class="zipcode"]/text()').extract_first())
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//div[@class="location-details"]//a/text()').extract_first())
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('./div[@class="location-details"]/text()').extract())
				for hour in hour_list:
					h_temp += hour + ', '
				item['store_hours'] = h_temp[:-2]
				yield item
			except:
				pass	

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
