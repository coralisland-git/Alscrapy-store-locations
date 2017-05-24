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

class pigglywiggly(scrapy.Spider):
	name = 'pigglywiggly'
	domain = 'https://www.pigglywiggly.com'
	history = ['']

	def start_requests(self):
		
		init_url  = 'http://www.pigglywiggly.com/store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@class="item-list"]//ul/li')
		for state in state_list:
			url = state.xpath('.//a/@href').extract_first()
			link_url = self.domain + url
			yield scrapy.Request(url=link_url, callback=self.parse_page)
	
	def parse_page(self, response):
		print('....parse_page checking........')
		store_list = response.xpath('//div[@class="item-list"]//ul//li')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//div[@class="street-address"]/text()'))
			item['city'] = self.validate(store.xpath('.//span[@class="locality"]/text()'))
			item['state'] = self.validate(store.xpath('.//span[@class="region"]/text()'))
			item['zip_code'] = self.validate(store.xpath('.//span[@class="postal-code"]/text()'))
			item['country'] = self.validate(store.xpath('.//div[@class="country-name"]/text()'))
			item['phone_number'] = self.validate(store.xpath('.//span[@class="field-content"]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			item['store_hours'] = ''
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item


	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''