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

class mountainmikespizza(scrapy.Spider):
	name = 'mountainmikespizza'
	domain = 'http://www.mountainmikespizza.com/'
	history = []

	def start_requests(self):
		init_url  = 'http://www.mountainmikespizza.com/locations.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[@id="main-content"]//table[2]//tr')
		for store in store_list:
			address = self.validate(store.xpath('.//td[1]/text()'))
			if address != '' :
				address = address.split(',')
				item = ChainItem()
				item['store_name'] = ''
				item['store_number'] = ''
				item['address'] = address[0]
				item['address2'] = ''
				item['city'] = address[1]
				item['state'] = address[2].strip().split(' ')[0]
				item['zip_code'] = address[2].strip().split(' ')[1]
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//td[2]/text()'))
				item['latitude'] = ''
				item['longitude'] = ''
				item['store_hours'] = ''
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''