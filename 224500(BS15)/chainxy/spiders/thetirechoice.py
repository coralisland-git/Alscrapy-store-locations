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

class thetirechoice(scrapy.Spider):
	name = 'thetirechoice'
	domain = 'http://locations.thetirechoice.com/'
	history = []

	def start_requests(self):
		init_url = 'http://locations.thetirechoice.com/fl.html'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		city_list = response.xpath('//a[@class="c-directory-list-content-item-link"]/@href').extract()
		for city in city_list:
			city = self.domain + city
			yield scrapy.Request(url=city, callback=self.parse_city)

	def parse_city(self, response):
		store_list = response.xpath('//a[@class="c-location-grid-item-link"]/@href').extract()
		if len(store_list) != 0:
			for store in store_list:
				if '/fl' in store:
					store = self.domain + store[3:]
					yield scrapy.Request(url=store, callback=self.parse_city)
		else:
			try:
				item = ChainItem()
				item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
				item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
				item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
				item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
				item['country'] = 'United States'
				item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
				item['latitude'] = self.validate(response.xpath('//meta[@itemprop="latitude"]/@content').extract_first())
				item['longitude'] = self.validate(response.xpath('//meta[@itemprop="longitude"]/@content').extract_first())
				h_temp = ''
				hour_list = response.xpath('//table[@class="c-location-hours-details"]//tr')
				for hour in hour_list:
					ho = ''
					for temp in self.eliminate_space(hour.xpath('.//text()').extract()):
						ho += temp + ' '
					h_temp += ho + ', '
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