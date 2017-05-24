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

class mariecallenders(scrapy.Spider):
	name = 'mariecallenders'
	domain = 'http://www.mariecallenders.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.mariecallenders.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//ul[@class="state-menu"]//a/@href').extract()
		for state in state_list:
			state_url = response.url + state
			yield scrapy.Request(url=state_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//section[@class="listing"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h3/text()').extract_first())
			item['address'] = self.validate(store.xpath('.//address//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//address//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(store.xpath('.//address//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(store.xpath('.//address//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//address//span[@itemprop="telephone"]/text()').extract_first())
			item['store_hours'] = self.validate(store.xpath('.//dt[1]/text()').extract_first())
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''