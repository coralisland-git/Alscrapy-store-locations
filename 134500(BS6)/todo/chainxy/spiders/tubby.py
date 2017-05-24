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
import usaddress

class tubby(scrapy.Spider):
	name = 'tubby'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://tubbys.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//li[@class="fusion-builder-row fusion-row"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h4/text()').extract_first())
				address = self.validate(store.xpath('.//address/text()').extract_first())
				addr = usaddress.parse(address)
				item['city'] = ''
				item['address'] = ''
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
							item['state'] = temp[0]
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0]
					else :
						item['address'] += temp[0] + ' '
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//a[2]/text()').extract_first())		
				yield item
			except:
				pass		

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''