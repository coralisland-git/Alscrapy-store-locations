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

class backyardburge(scrapy.Spider):
	name = 'backyardburge'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.backyardburgers.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//a[@class="button -text-highlight"]')
		for store in store_list:
			if 'details' in self.validate(store.xpath('./text()').extract_first()).lower():
				yield scrapy.Request(url=store.xpath('./@href').extract_first(), callback=self.parse_page)
		
	
	def parse_page(self, response):
		item = ChainItem()
		item['address'] = self.validate(response.xpath('//div[@class="street-address"]/text()').extract_first())
		item['city'] = self.validate(response.xpath('//span[@class="locality"]/text()').extract_first())
		item['state'] = self.validate(response.xpath('//abbr[@class="region"]/text()').extract_first())
		item['zip_code'] = self.validate(response.xpath('//span[@class="postal-code"]/text()').extract_first())
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//div[@class="tel"]//a/text()').extract_first())
		h_temp =''
		hour_list = response.xpath('//article[@class="blog"]//p[2]/text()').extract()
		for hour in hour_list:
			h_temp	+= self.validate(hour) + ', '
		item['store_hours'] = h_temp[:-2]
		yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''