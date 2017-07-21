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

class beallstx(scrapy.Spider):
	name = 'beallstx'
	domain = 'http://stores.stage.com/'
	history = []

	def start_requests(self):
		init_url = 'http://stores.stage.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_page)

	def parse_page(self, response):
		city_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		if city_list:
			for city in city_list :
				city_link = self.domain + city
				yield scrapy.Request(url=city_link, callback=self.parse_page)

		store_list = response.xpath('//ul[@class="location-list"]//a[@class="decorated-link location-card-visit-link location-card-link"]/@href').extract()
		if store_list:
			for store in store_list:
				store_link = self.domain + store[3:]
				header = {
					'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
					'Accept-Encoding':'gzip, deflate'
				}
				yield scrapy.Request(url=store_link, headers=header, callback=self.parse_page)
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="c-location-title"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			item['latitude'] = self.validate(response.xpath('//meta[@itemprop="latitude"]/@content').extract_first())
			item['longitude'] = self.validate(response.xpath('//meta[@itemprop="longitude"]/@content').extract_first())
			h_temp = ''
			hour_list = response.xpath('//table[@class="c-location-hours-details"]//tr[@class="c-location-hours-details-row js-day-of-week-row highlight-text "]')
			for hour in hour_list:
				temp = ''
				for ho in self.eliminate_space(hour.xpath('.//text()').extract()):
					temp += ho + ' '
				h_temp += temp + ', '
			item['store_hours'] = h_temp[:-2]
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
