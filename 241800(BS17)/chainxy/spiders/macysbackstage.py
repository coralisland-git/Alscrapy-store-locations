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

class macysbackstage(scrapy.Spider):
	name = 'macysbackstage'
	domain = 'https://stores.macysbackstage.com/'
	history = []

	def start_requests(self):
		init_url = 'https://stores.macysbackstage.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="container"]//h5[@class="c-location-grid-item-title"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.str_concat(response.xpath('//h1[@class="c-location-title"]//text()').extract(), ' ')
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]//text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]//text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]//text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]//text()').extract_first())
			item['latitude'] = self.validate(response.xpath('//meta[@itemprop="latitude"]/@content').extract_first())
			item['longitude'] = self.validate(response.xpath('//meta[@itemprop="longitude"]/@content').extract_first())
			h_temp = ''
			hour_list = response.xpath('//tr[contains(@class, "c-location-hours-details-row")]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//td[@class="c-location-hours-details-row-day"]/text()').extract_first()) + ' ' 
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-details-row-intervals-instance-open"]/text()').extract_first()) + ' - '
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-details-row-intervals-instance-close"]/text()').extract_first()) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace(',','')
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