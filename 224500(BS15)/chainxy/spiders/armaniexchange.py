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

class armaniexchange(scrapy.Spider):
	name = 'armaniexchange'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.armaniexchange.com/us/store_location_section'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@class, "text-content")]//li')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['store_name'] = detail[0]
				if len(detail) == 4:
					item['address'] = detail[1]
					addr = detail[2].split(',')
					item['city'] = self.validate(addr[0].strip())
					sz = addr[1].strip().split(' ')
					state = ''
					for temp in sz[:-1]:
						state += temp + ' '
					item['state'] = self.validate(state)
					item['zip_code'] = self.validate(sz[-1])
					item['country'] = 'United States'
					item['phone_number'] = detail[3]
				elif len(detail) == 5:
					item['address'] = detail[1] + ', ' + detail[2]
					addr = detail[3].split(',')
					item['city'] = self.validate(addr[0].strip())
					sz = addr[1].strip().split(' ')
					state = ''
					for temp in sz[:-1]:
						state += temp + ' '
					item['state'] = self.validate(state)
					item['zip_code'] = self.validate(sz[-1])
					item['country'] = 'United States'
					item['phone_number'] = detail[4]
				if 'ca/' not in item['state'].lower():
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
			if self.validate(item) != '' and 'opening' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp