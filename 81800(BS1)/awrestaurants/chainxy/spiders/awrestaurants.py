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

class todo(scrapy.Spider):
	name = 'awrestaurants'
	domain = 'https://www.awrestaurants.com/'
	history = ['']

	# def __init__(self):

	def start_requests(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
		    location_list = json.load(data_file)
		for location in location_list:
			init_url  = 'http://www.awrestaurants.com/locations?zipcode='+location['city']+', '+location['state']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)
		store_list = response.xpath('.//div[@class="location-info"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//div[@class="location-address inline"]/text()'))
			item['address2'] = ''
			# print("-===========================				", self.validate(store.xpath('.//span[@class="location-city inline"]')))
			item['city'] = self.validate(store.xpath('.//span[@class="location-city inline"]')).split(',')[0].split('>')[1]
			item['state'] = self.validate(store.xpath('.//span[@class="location-city inline"]')).split(',')[1].strip().split(' ')[0]
			item['zip_code'] = self.validate(store.xpath('.//span[@class="location-city inline"]')).split(',')[1].strip().split(' ')[1]
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@class="location-phone inline"]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			item['store_hours'] = ''
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['phone_number'] not in self.history:
				yield item
				self.history.append(item['phone_number'])

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''
