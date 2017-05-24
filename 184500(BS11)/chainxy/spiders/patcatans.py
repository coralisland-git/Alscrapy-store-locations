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

class patcatans(scrapy.Spider):
	name = 'patcatans'
	domain = 'http://www.patcatans.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.patcatans.com/craft-store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="location-list"]//a[@class="location-title-link"]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//ul[@class="location-map-item-list"]')
			item['address'] = self.validate(store.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''			
			hour_list = store.xpath('.//ul[@class="location-map-hours-list"][1]//li')
			if hour_list:
				h_temp = 'Normal Hours : '	
				for hour in hour_list:
					hour = self.eliminate_space(hour.xpath('.//text()').extract())
					for temp in hour:
						h_temp += temp + ' '
					h_temp += ', '
			hour_list = store.xpath('.//ul[@class="location-map-hours-list"][2]//li')
			if hour_list:
				h_temp += 'Frame Shop Hours : '
				for hour in hour_list:
					hour = self.eliminate_space(hour.xpath('.//text()').extract())
					for temp in hour:
						h_temp += temp + ' '
					h_temp += ', '
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