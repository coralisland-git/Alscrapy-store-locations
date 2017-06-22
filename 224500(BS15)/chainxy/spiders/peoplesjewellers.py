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

class peoplesjewellers(scrapy.Spider):
	name = 'peoplesjewellers'
	domain = 'http://www.mystore411.com'
	history = []
	count = 0
	ind = 0
	proxy_list = [	'https://198.50.219.230:8080',
					'https://158.69.223.147:3128',
					'https://167.114.35.69:8080',
					'https://144.217.201.17:8080',
					'https://144.217.189.144:3128',
					'https://144.217.170.87:3128',
					'https://198.50.219.239:80',
					'https://149.56.8.228:8080',
					'https://149.56.201.164:80',
					'https://158.69.31.45:3128'
					]
	
	def start_requests(self):
		init_url = 'http://www.mystore411.com/store/listing/2945/Canada/Peoples-Jewellers-store-locations'		
		yield scrapy.Request(url=init_url, callback=self.parse_state, meta = {'proxy':self.proxy_list[self.ind]}) 

	def parse_state(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//table[@class="table1"][1]//a/@href').extract()
		for state in state_list:
			state_link = self.domain + state
			self.count += 1
			if self.count % 20 == 0:
				self.ind += 1
			yield scrapy.Request(url=state_link, callback=self.parse_store, meta = {'proxy':self.proxy_list[self.ind]})
 
	def parse_store(self, response):
		store_list = response.xpath('//td[@class="dotrow"]//a')
		for store in store_list:
			store_name = store.xpath('./text()').extract_first()
			store_link = self.domain + store.xpath('./@href').extract_first()
			self.count += 1
			if self.count % 20 == 0:
				self.ind += 1
			yield scrapy.Request(url=store_link, callback=self.parse_page, meta={'store_name':store_name, 'proxy':self.proxy_list[self.ind]})

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			address_list = self.eliminate_space(response.xpath('//span[@itemprop="streetAddress"]//text()').extract())
			a_temp = ''
			for address in address_list:
				a_temp += address + ' '
			item['address'] = self.validate(a_temp)			
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
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