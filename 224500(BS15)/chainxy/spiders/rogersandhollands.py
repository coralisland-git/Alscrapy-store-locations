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

class rogersandhollands(scrapy.Spider):
	name = 'rogersandhollands'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://rogersandhollands.com/effy-locations'	
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table//td')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['store_name'] = detail[1]
				addr = detail[2].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				item['country'] = 'United States'
				item['phone_number'] = detail[3]
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
