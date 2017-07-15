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

class batteriesplus(scrapy.Spider):
	name = 'batteriesplus'
	domain = 'https://www.batteriesplus.com/'
	history = ['']
	
	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):

		for location in self.location_list:
			init_url  = 'https://www.batteriesplus.com/store-locator?search='+location['city']+'&lat=&lng='
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
			
		store_list = response.xpath('.//div[@class="nano-content"]//div[@class="user-bar-listing-box"]')
		for store in store_list:
			try:
				item = ChainItem()
				opening_soon = store.xpath('.//div[@class="store-box-info"]//span[@class="pull-right txt-green"]/text()').extract_first()
				if opening_soon is not None:
					item['store_number'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[1].split('#')[1].strip()
					item['address'] = store.xpath('.//div[@class="listing-address"]/text()').extract_first().strip()
					item['city'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[0].strip()
					item['state'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[1].split('#')[0].strip()
					item['store_hours'] = opening_soon
				else: 
					item['store_number'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[1].split('#')[1].strip()
					item['address'] = store.xpath('.//div[@class="listing-address"]/text()').extract_first().strip()
					item['city'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[0].strip()
					item['state'] = store.xpath('.//strong[@class="listing-city"]//span/text()').extract_first().strip().split(',')[1].split('#')[0].strip()
					item['phone_number'] = store.xpath('.//div[@class="listing-phone"]//strong[1]/text()').extract_first() + store.xpath('.//div[@class="listing-phone"]//span/text()').extract_first().strip()
					item['phone_number'] = item['phone_number'] + ", " + store.xpath('.//div[@class="listing-phone"]//strong[2]/text()').extract_first() + store.xpath('.//div[@class="listing-phone"]/text()').extract()[4].strip()
					h_temp = ''
					hour_list = store.xpath('.//div[@class="listing-hours"]//span')
					for hour in hour_list : 
						weekday = hour.xpath('.//strong/text()').extract_first().strip()
						weektime = hour.xpath('./text()').extract_first().strip()
						h_temp = h_temp + weekday + weektime
					item['store_hours'] = h_temp
				item['country'] = 'United States'
				if item['store_number']+item['address'] in self.history:
					continue
				self.history.append(item['store_number']+item['address'])
				yield item		
			except:
				pass
