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

class rue(scrapy.Spider):
	name = 'rue'
	domain = 'https://stores.rue21.com/'
	history = []

	def start_requests(self):
		init_url  = 'https://stores.rue21.com/index.html'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			if len(state.split('/')) == 1:
				yield scrapy.Request(url=state_link, callback=self.parse_city)	
			elif len(state.split('/')) == 2:				
				yield scrapy.Request(url=state_link, callback=self.parse_store)
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_page)

	def parse_city(self, response):
		city_list = response.xpath('//li[@class="c-directory-list-content-item"]//a/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			if len(city.split('/')) == 2:
				yield scrapy.Request(url=city_link, callback=self.parse_store)
			else:
				yield scrapy.Request(url=city_link, callback=self.parse_page)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="c-location-grid-item"]//a[1]/@href').extract()
		for store in store_list:
			store_link = self.domain + store[3:]
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@class="location-name"]/text()')) + ' ' + self.validate(response.xpath('//span[@class="location-geomodifier"]/text()'))
			item['address'] = self.validate(response.xpath('//span[@class="c-address-street-1"]/text()'))
			item['address2'] = self.validate(response.xpath('//span[@class="c-address-street-2"]/text()'))
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()'))
			item['state'] = self.validate(response.xpath('//abbr[@class="c-address-state"]/text()'))
			item['zip_code'] = self.validate(response.xpath('//span[@class="c-address-postal-code"]/text()'))
			item['country'] = self.validate(response.xpath('//abbr[contains(@class, "c-address-country-name")]/text()'))
			item['phone_number'] = self.validate(response.xpath('//span[@id="telephone"]/text()'))
			h_temp = ''
			hour_list = response.xpath('//table[@class="c-location-hours-details"]//tbody//tr')
			for hour in hour_list:
				temp = hour.xpath('.//text()').extract()
				for te in temp:
					h_temp += te.strip() + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pass

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''