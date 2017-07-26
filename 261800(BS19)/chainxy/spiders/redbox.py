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

class redbox(scrapy.Spider):
	name = 'redbox'
	domain = 'https://stores.buybuybaby.com/'
	history = []

	def start_requests(self):
		init_url = 'http://www.redbox.com/locations/state'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="store-column"]//a/@href').extract()
		for state in state_list : 
			yield scrapy.Request(url=state, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="store-column"]//a/@href').extract()
		for city in city_list :
			yield scrapy.Request(url=city, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="store-column"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('.//div[@class="store-name"]/text()').extract_first())
			detail = self.eliminate_space(response.xpath('.//div[@class="store-address"]/p//text()').extract())
			address = ''
			for de in detail:
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
			yield item		
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\n',' ').replace('\r',' ').replace('  ','')
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
