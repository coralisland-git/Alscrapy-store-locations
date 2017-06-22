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
import pdb

class vineyardvines(scrapy.Spider):
	name = 'vineyardvines'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.vineyardvines.com/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store_content"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h4[@class="store_name"]/text()').extract_first())
				detail = self.eliminate_space(store.xpath('.//p[@class="store_content_reg"]//text()').extract())
				address = ''
				for de in detail:
					if '(' in de or len(de.split('-')) == 3:
						item['phone_number'] = de
					else:
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
				item['country'] = 'United States'
				try:
					item['store_hours'] = self.str_concat(self.eliminate_space(store.xpath('.//p[@class="store_content_sml"]//text()').extract()), ', ')
				except:
					pass
				yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\t','').replace('\r', '')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp