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

class urbanplates(scrapy.Spider):
	name = 'urbanplates'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://urbanplates.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//footer//div[@class="footer"]//div[@class="footer_quad"]')
		for store in store_list:
			detail = self.eliminate_space(store.xpath('.//text()').extract())
			try:
				item = ChainItem()
				item['store_name'] = detail[0]
				if len(detail) == 4:
					item['address'] = detail[1]
					addr = detail[2].split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['phone_number'] = detail[3]
				elif len(detail) == 5:
					item['address'] = detail[1] + ' ' + detail[2]
					addr = detail[3].split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['phone_number'] = detail[4]
				item['country'] = 'United States'
				h_temp = ''
				hour_list = self.eliminate_space(response.xpath('//div[@class="panel-grid-cell"]//text()').extract())
				for hour in hour_list[:2]:
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
			if self.validate(item) != '' and 'hours' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp