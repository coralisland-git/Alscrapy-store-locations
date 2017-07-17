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

class fekkai(scrapy.Spider):
	name = 'fekkai'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.fekkai.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//li[@class="por"][1]//ul//a/@href').extract()
		for store in store_list[:8]:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="ma20 pl w400"]//text()').extract())
			item['store_name'] = detail[0]
			item['address'] = detail[6]
			item['city'] = detail[7].replace(',','')
			item['state'] = detail[8]
			item['zip_code'] = detail[9]
			item['country'] = 'United States'
			item['phone_number'] = detail[4]
			h_temp = ''
			for de in detail:
				if 'day:' in de:
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
			if self.validate(item) != '' and 'GROUP RESERVATIONS' not in self.validate(item) and 'Brazilian Court Hotel' != self.validate(item):
				tmp.append(self.validate(item))
		return tmp