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

class a1selfstorage(scrapy.Spider):
	name = 'a1selfstorage'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.a1storage.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//td[@class="directory-location-name p-name"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//footer//h4[@class="p-name"]//span[@class="notranslate"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//footer//span[@class="p-street-address street-address"]//span[@class="notranslate"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//footer//span[@class="p-locality locality"]//span[@class="notranslate"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//footer//span[@class="p-region region"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//footer//span[@class="p-postal-code postal-code"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//footer//p[@class="phone"]//span[@class="p-tel tel"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="office-hours"]//text()').extract())
			for hour in hour_list:
				if 'hour' not in hour.lower():
					h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass	

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