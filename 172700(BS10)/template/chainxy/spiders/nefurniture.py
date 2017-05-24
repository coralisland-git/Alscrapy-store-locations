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
import pdb
import tokenize
import token
from StringIO import StringIO

class nefurniture(scrapy.Spider):
	name = 'nefurniture'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_US = json.load(data_file)

		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_CA = json.load(data_file)



	def start_requests(self):
		init_url = 'https://www.lanefurniture.com/store-locator/'
		for location in self.location_list_US:
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/x-www-form-urlencoded"
			}
			formdata = {
				"zip":location['city'],
				"radius":"500"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body) 

		for location in self.location_list_CA:
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/x-www-form-urlencoded"
			}
			formdata = {
				"zip":location['city'],
				"radius":"500"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body) 


	def body(self, response):
		store_list = response.xpath('//div[@class="aw-storelocator-item"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[1]//b/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//div[2]/text()').extract_first())
				address = self.validate(store.xpath('.//div[3]/text()').extract_first())
				addr = self.eliminate_space(address.split(','))
				item['city'] = self.validate(addr[0].strip())
				sz = addr[1].strip().split(' ')
				item['state'] = sz[0]
				item['zip_code'] = ''
				for cnt in range(1, len(sz)):
					item['zip_code'] += sz[cnt] + ' '
				item['country'] = addr[2]
				item['phone_number'] = self.validate(store.xpath('.//div[4]/text()').extract_first())
				if item['store_name']+item['phone_number'] not in self.history:
					self.history.append(item['store_name']+item['phone_number'])
					yield item		
			except:
				pdb.set_trace()	


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