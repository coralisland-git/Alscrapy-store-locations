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

class bomgaars(scrapy.Spider):
	name = 'bomgaars'
	domain = 'http://www.bomgaars.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.bomgaars.com/contact-us/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//li[@class="list_item"]//div[@class="metadata1 title"]//a/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@id="main-content-without-navigation"]//div//h1/text()').extract_first())
			address = self.eliminate_space(response.xpath('//div[@class="metadata1 title"]//text()').extract())
			item['address'] = address[0]
			addr = address[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			hour_list = response.xpath('//div[@class="location-extra-fields"]//div[@class="extra-field"]')
			item['phone_number'] = self.validate(hour_list[1].xpath('.//div[@class="extra-field-value"]/text()').extract_first())
			hour_list = self.eliminate_space(hour_list[len(hour_list)-1].xpath('.//div[@class="extra-field-value"]//text()').extract())
			h_temp = ''
			for hour in hour_list:
				if ':' in self.validate(hour):
					h_temp += self.validate(hour) + ', '
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''