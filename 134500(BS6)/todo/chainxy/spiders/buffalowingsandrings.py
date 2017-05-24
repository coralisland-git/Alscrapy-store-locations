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

class buffalowingsandrings(scrapy.Spider):
	name = 'buffalowingsandrings'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.buffalowingsandrings.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@class, "cardgrid__card location__card")]')
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//a[1]/text()').extract_first())
			detail = store.xpath('.//address/text()').extract()
			item['address'] = self.validate(detail[0])
			addr = detail[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail[2])
			h_temp = ''
			hour_list = store.xpath('.//p/text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '':
					h_temp += self.validate(hour) + ', '
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = '0'
			if 'coming' in item['store_hours'].lower():
				item['coming_soon'] = '1'
				item['store_hours'] = ''
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''