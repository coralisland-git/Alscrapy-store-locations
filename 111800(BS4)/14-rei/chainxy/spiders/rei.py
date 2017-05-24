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
import unicodedata

class rei(scrapy.Spider):
	name = 'rei'
	domain = 'https://www.rei.com'
	history = []

	def start_requests(self):
		
		init_url = 'https://www.rei.com/map/store'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@class="store-name-link"]/@href').extract()
		for store in store_list:
			detail_url = self.domain + store
			yield scrapy.Request(url=detail_url, callback=self.parse_page)
	def parse_page(self, response):

		item = ChainItem()
		item['store_name'] = ''
		item['store_number'] = ''
		item['address'] = self.validate(response.xpath('//span[@data-ui="address1"]/text()'))
		item['address2'] = ''
		item['city'] = self.validate(response.xpath('//span[@data-ui="locality"]/text()'))[:-1]
		item['state'] = self.validate(response.xpath('//span[@data-ui="region"]/text()'))
		item['zip_code'] = self.validate(response.xpath('//span[@data-ui="postalCode"]/text()'))
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//span[@data-ui="telephone1"]/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = response.xpath('//div[@data-ui="storeHours"]//div[@class="row"]')
		for hour in hour_list:
			h_temp += self.validate(hour.xpath('.//strong/text()')) + ' ' + self.format(self.validate(hour.xpath('.//div/text()')))
			if self.format(self.validate(hour.xpath('.//div/text()'))) != '':
				h_temp += ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item
			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace(';','')
		except:
			return ''

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''