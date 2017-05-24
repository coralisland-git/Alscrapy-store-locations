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

class niceneasy(scrapy.Spider):
	name = 'niceneasy'
	domain = 'http://niceneasy.com'
	history = []

	def start_requests(self):
		init_url = 'http://niceneasy.com/StoresList/1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store-item"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

		pagenation = response.xpath('//a[@title="Go to next page"]/@href').extract_first()
		if pagenation is not None:
			pagenation = self.domain + pagenation
			yield scrapy.Request(url=pagenation, callback=self.body)

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//h1[@class="store-page-header-store-name-h1"]/text()').extract_first())
		item['address'] = self.validate(response.xpath('//span[@class="store-street-address"]/text()').extract_first())
		item['city'] = self.validate(response.xpath('//span[@class="store-address-city"]/text()').extract_first())
		item['state'] = self.validate(response.xpath('//span[@class="store-address-state"]/text()').extract_first())
		item['zip_code'] = self.validate(response.xpath('//span[@class="store-address-zip"]/text()').extract_first())
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//span[@class="store-address-phone-number"]/text()').extract_first())
		hour_list = self.eliminate_space(response.xpath('//div[@class="store-hours-container-div"]//text()').extract())
		h_temp = ''
		for hour in hour_list:
			h_temp += hour + ' '
		item['store_hours'] = self.validate(h_temp)
		yield item


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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''