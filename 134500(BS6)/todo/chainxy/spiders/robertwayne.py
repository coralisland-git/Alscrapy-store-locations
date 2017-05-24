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
import pdb
import usaddress

class robertwayne(scrapy.Spider):
	name = 'robertwayne'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.robertwayne.com/info/storelocations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="modal-content"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="modal-header"]//h4/text()').extract_first())
			address = self.validate(store.xpath('.//p[3]/text()').extract_first())
			addr = usaddress.parse(address)
			item['address'] = ''
			item['city'] = ''
			item['zip_code'] = ''
			try:
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0]
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0]
					else:
						item['address'] += temp[0].replace(',', '') + ' '
			except:
				pdb.set_trace()
			item['phone_number'] = self.validate(store.xpath('.//p[1]/text()').extract_first())
			item['store_hours'] = self.validate(store.xpath('.//p[2]/text()').extract_first())
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''