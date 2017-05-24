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

class solasalonstudios(scrapy.Spider):
	name = 'solasalonstudios'
	domain = 'https://www.solasalonstudios.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.solasalonstudios.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//input[@name="marker"]')
		for store in store_list:
			try:
				url = self.domain + self.validate(store.xpath('./@data-url').extract_first())
				request = scrapy.Request(url=url, callback=self.parse_page)
				request.meta['store_name'] = self.validate(store.xpath('./@data-name').extract_first())
				address = self.validate(store.xpath('./@data-saddress').extract_first())
				request.meta['address'] = ''
				request.meta['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						request.meta['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						request.meta['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						request.meta['zip_code'] = temp[0].replace(',','')
					else:
						request.meta['address'] += temp[0].replace(',', '') + ' '
				request.meta['country'] = 'United States'
				request.meta['latitude'] = self.validate(store.xpath('./@value').extract_first().split(',')[0])
				request.meta['longitude'] = self.validate(store.xpath('./@value').extract_first().split(',')[1])
				yield request
			except:
				pdb.set_trace()		

	def parse_page(self, response):
		try:
			phone = self.validate(response.xpath('//a[@class="tel"]/text()').extract_first())
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			item['address'] = response.meta['address']
			item['city'] = response.meta['city']
			item['state'] = response.meta['state']
			item['zip_code'] = response.meta['zip_code']
			item['country'] = response.meta['country']
			item['latitude'] = response.meta['latitude']
			item['longitude'] = response.meta['longitude']
			item['phone_number'] = phone
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