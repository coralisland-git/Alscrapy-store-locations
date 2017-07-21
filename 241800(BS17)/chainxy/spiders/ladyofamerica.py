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

class ladyofamerica(scrapy.Spider):
	name = 'ladyofamerica'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.ladyofamerica.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="club"]//div[@class="content-accordion"][1]//p')
		for store in store_list[:3]:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				address = ''
				item['phone_number'] = ''
				for de in detail[:-1]:
					address += de + ', '
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['phone_number'] = detail[-1]
				item['country'] = 'United States'
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