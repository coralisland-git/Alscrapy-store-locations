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

class rockinghamcoop(scrapy.Spider):
	name = 'rockinghamcoop'
	domain = 'https://rockinghamcoop.com/'
	history = []

	def start_requests(self):
		init_url = 'https://rockinghamcoop.com/locations.html'
		yield scrapy.Request(url=init_url, callback=self.body) 
	def body(self, response):
		store_list = response.xpath('//a[@class="nonblock nontext Button-Normal shadow rounded-corners clearfix colelem shared_content"]//@href').extract()
												# 'nonblock nontext shadow rounded-corners Button-Normal clearfix colelem'
		for store in store_list :
			store_link  = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		detail = self.eliminate_space(response.xpath('//div[@class="ts-p--Main-Body-Text clearfix grpelem shared_content"]//text()').extract())
		pdb.set_trace()

		# # pdb.set_trace()
		# for store in store_list:
			
			# item = ChainItem()
			# item['store_name'] = self.validate(store['name'])
			# item['store_number'] = self.validate(store['store_number'])
			# item['address'] = self.validate(store['address'])
			# item['address2'] = self.validate(store['crossStreet'])
			
			# addr = address.split(',')
			# item['city'] = self.validate(addr[0].strip())
			# item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			# item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())


			# item['city'] = self.validate(store['city'])
			# item['state'] = self.validate(store['state'])
			# item['zip_code'] = self.validate(store['zip'])
			# item['country'] = self.validate(store['country'])
			# item['phone_number'] = self.validate(store['phone'])
			# item['latitude'] = self.validate(store['latitude'])
			# item['longitude'] = self.validate(store['longitude'])
			# item['store_hours'] = self.validate(store['hours'])
			# item['store_type'] = ''
			# item['other_fields'] = ''
			# item['coming_soon'] = ''
			# if item['store_number'] not in self.history:
			# 	self.history.append(item['store_number'])
			# 	yield item			


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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''