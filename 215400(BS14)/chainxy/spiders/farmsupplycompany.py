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

class farmsupplycompany(scrapy.Spider):
	name = 'farmsupplycompany'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.farmsupplycompany.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="location cf"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h2/text()').extract_first())
				detail = self.eliminate_space(store.xpath('.//p[1]//text()').extract())
				item['address'] = detail[0]				
				item['country'] = 'United States'
				item['phone_number'] = detail[1]
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//p[3]//text()').extract())
				for hour in hour_list[1:]:
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp
