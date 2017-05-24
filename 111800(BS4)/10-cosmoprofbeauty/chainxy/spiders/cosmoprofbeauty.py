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

class cosmoprofbeauty(scrapy.Spider):
	name = 'cosmoprofbeauty'
	domain = 'https://stores.cosmoprofbeauty.com'
	history = []

	def start_requests(self):
		init_url  = 'https://stores.cosmoprofbeauty.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="mapListItemWrap"]//a[@class="gaq-link"]/@href').extract()
		for state in state_list : 
			yield scrapy.Request(url=state, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="mapListItemWrap"]//a[@class="gaq-link"]/@href').extract()
		for city in city_list :
			yield scrapy.Request(url=city, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="rio-list-links"]//a[contains(@data-gaq, "View Details")]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[contains(@class, "rio-indyDescription")]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('.//div[@class="locationName"]/text()')).split('#')[0].strip()
			item['store_number'] = self.validate(detail.xpath('.//div[@class="locationName"]/text()')).split('#')[1].strip()
			item['address'] = self.validate(detail.xpath('.//div[@class="addr"][1]/text()'))
			item['address2'] = self.validate(detail.xpath('.//div[@class="addr"][2]/text()'))
			item['city'] = self.validate(detail.xpath('.//div[@class="csz"]//span[1]/text()'))
			item['state'] = self.validate(detail.xpath('.//div[@class="csz"]//span[2]/text()'))
			item['zip_code'] = self.validate(detail.xpath('.//div[@class="csz"]//span[3]/text()'))
			item['country'] = ''
			if len(item['zip_code']) > 5:
				item['country'] = 'Canada'
			else :
				if item['state'] == 'PR':
					item['country'] = 'Puert Rico'
				else :
					item['country'] = 'United States'
			item['phone_number'] = self.validate(detail.xpath('.//div[@class="phone"]//a/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = detail.xpath('//div[@class="day-hour-row"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//div[@class="daypart"]/text()')) + ' ' + self.validate(hour.xpath('.//div[@class="hours"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''