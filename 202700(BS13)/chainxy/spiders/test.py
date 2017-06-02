from __future__ import unicode_literals
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
import usaddress
import pdb
import time

class test(scrapy.Spider):
	name = 'test'
	domain = 'https://www.goodyearautoservice.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.goodyearautoservice.com/en-US/shop/_jcr_content/content/store_results.content?currentPage=1'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		with open('response.html', 'wb') as f:
			f.write(response.body)

	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//div[@class="store-page-masthead store-page-masthead__wrapper"]')
			item['store_name'] = self.validate(store.xpath('.//span[@itemprop="legalName"]/text()').extract_first())
			item['address'] = self.validate(store.xpath('.//p[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()).split(',')[0].strip()
			item['state'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()).split(',')[1].strip()
			item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//ul[@itemprop="openingHoursSpecification"]//li')
			for hour in hour_list:
				temp = self.eliminate_space(hour.xpath('.//text()').extract())
				for te in temp:
					h_temp += te.strip() + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp
