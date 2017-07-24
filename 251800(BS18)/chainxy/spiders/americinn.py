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

class americinn(scrapy.Spider):
	name = 'americinn'
	domain = 'https://www.americinn.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.americinn.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//ul[@class="state-list"]//li//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//ul[contains(@class, "cities listing")]//a/@href').extract()
		if store_list:
			for store in store_list:
				store_link = self.domain + store
				yield scrapy.Request(url=store_link, callback=self.parse_page)
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="page-heading"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]//span/text()').extract_first())
			if item['address'] != '':
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp
