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

class islandsrestau(scrapy.Spider):
	name = 'islandsrestau'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.islandsrestaurants.com/locations/search/%s?lat=%s&lng=%s' %(location['city'], str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//ul[@class="location-list"]//div[contains(@class, "node node-restaurant")]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h2[@class="restaurant-title"]//a/text()').extract_first())	
			item['address'] = self.validate(store.xpath('.//div[@class="address"]/text()').extract_first())	
			address = self.validate(store.xpath('.//div[@class="city-state-zip"]/text()').extract_first())	
			addr = address.split(',')
			item['city'] = addr[0].strip()
			item['state'] = addr[1].strip().split(' ')[0].strip()
			item['zip_code'] = addr[1].strip().split(' ')[1].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]//a/text()').extract_first())	
			h_temp = ''
			hour_list = store.xpath('.//div[@class="hours"]//text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '' and 'am' in self.validate(hour).lower():
					h_temp += self.validate(hour) +', '
			item['store_hours'] = h_temp[:-2]
			if item['phone_number'] == '':
				yield item	
			else:
				if item['phone_number'] not in self.history:
					self.history.append(item['phone_number'])
					yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''