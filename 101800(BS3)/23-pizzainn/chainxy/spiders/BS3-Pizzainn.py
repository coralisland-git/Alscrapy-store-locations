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

class BS3Pizzainn(scrapy.Spider):
	name = 'BS3-Pizzainn'
	domain = 'http://www.pizzainn.com/locations/'
	history = []
 
	def start_requests(self):
	
		init_url = 'http://www.pizzainn.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@id="locationsStateMap"]//map[@id="m_locations_state_map"]//area/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="loc-search-results"]//div[@class="row"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//span[@class="loc-name"]//a/text()'))
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//span[@class="loc-address-1"]/text()'))
			item['address2'] = self.validate(store.xpath('.//span[@class="loc-address-2"]/text()'))
			address = self.validate(store.xpath('.//span[@class="loc-address-3"]/text()')).split(',')
			item['city'] = address[0].strip()
			item['state'] = address[1].strip().split(' ')[0].strip()
			item['zip_code'] = address[1].strip().split(' ')[1].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@class="loc-phone"]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//span[@class="loc-hours"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('./text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('\n', '').replace('\r', '').replace(';','')
		except:
			return ''