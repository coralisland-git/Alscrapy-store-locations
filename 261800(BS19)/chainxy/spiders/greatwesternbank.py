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

class greatwesternbank(scrapy.Spider):
	name = 'greatwesternbank'
	domain = 'https://www.greatwesternbank.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.greatwesternbank.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="location-search-form"]//h3[@class="h4"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="single-col-container"]//h2//a/@href').extract()
		if store_list:
			for store in store_list:
				store_link = self.domain + store
				yield scrapy.Request(url=store_link, callback=self.parse_page)
		
	def parse_page(self, response):		
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="space-below"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//time[@itemprop="openingHours"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if item['address'] != '':
				yield item			
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace(';','')
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
