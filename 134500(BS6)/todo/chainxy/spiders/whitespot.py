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

class whitespot(scrapy.Spider):
	name = 'whitespot'
	domain = 'https://www.whitespot.ca'
	history = []

	def start_requests(self):
		init_url = 'https://www.whitespot.ca/locations.htm/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@id="sidebar-bottom"]//li//a/@href').extract()
		for state in state_list:
			state_url = self.domain + state
			yield scrapy.Request(url=state_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//div[contains(@class, "view-locations")]//div[contains(@class, "views-row")]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[@class="location-name"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//div[@class="location-street"]/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//div[@class="location-city-province"]/text()').extract_first()).split(',')[0].strip()
				item['state'] = self.validate(store.xpath('.//div[@class="location-city-province"]/text()').extract_first()).split(',')[1].strip()
				item['zip_code'] = self.validate(store.xpath('.//div[@class="location-postal-code"]/text()').extract_first())
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store.xpath('.//div[@class="location-phone"]/text()').extract_first())
				h_temp = ''
				hour_list = store.xpath('.//div[contains(@class, "views-field-field-hours-of-operation")]//div[@class="field-content"]//text()').extract()
				for hour in hour_list:	
					if self.validate(hour) != '':
						h_temp += self.validate(hour) +', '
				item['store_hours'] = h_temp[:-2]
				yield item			
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(';','').replace('\n', '')
		except:
			return ''