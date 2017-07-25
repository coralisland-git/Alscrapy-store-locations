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

class vallartasupermarkets(scrapy.Spider):
	name = 'vallartasupermarkets'
	domain = 'http://www.vallartasupermarkets.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.vallartasupermarkets.com/en/store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store storeListing"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = self.eliminate_space(response.xpath('//div[@class="store columnMiddle1"]//text()').extract())
		try:
			item = ChainItem()
			item['store_name'] = detail[0]
			item['address'] = detail[2]			
			addr = detail[3].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			h_temp = ''
			for de in detail:
				if '(' in de and 'P:' in de:
					item['phone_number'] = de.replace('P:', '').strip()
				elif 'day' in de and ':' in de:
					h_temp += de + ', '
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