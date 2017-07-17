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

class superkingmarkets(scrapy.Spider):
	name = 'superkingmarkets'
	domain = 'https://superkingmarkets.com/'
	history = []

	def start_requests(self):
		init_url = 'https://superkingmarkets.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		obj = response.xpath('//ul[@class="toggle-footer list-group bullet"]')
		store_list = obj[1].xpath('.//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_detail)

	def parse_detail(self, response):
		detail = self.eliminate_space(response.xpath('//div[@class="panel-body"]//text()').extract())
		try:
			item = ChainItem()
			item['store_name'] = response.xpath('//h1/text()').extract_first()
			item['address'] = detail[0]		
			addr = detail[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = detail[3].split('Phone :')[1].strip()
			item['store_hours'] = detail[2]
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