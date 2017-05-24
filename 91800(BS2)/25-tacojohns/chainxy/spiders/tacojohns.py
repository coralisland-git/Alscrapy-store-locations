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

class tacojohns(scrapy.Spider):
	name = 'tacojohns'
	domain = 'http://locations.tacojohns.com/'
	history = ['']

	def start_requests(self):
		
		init_url  = 'http://locations.tacojohns.com/index.html'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		print('---------------- checking ..................')
		state_list = response.xpath('//ul[@class="c-directory-list-content"]//li[@class="c-directory-list-content-item"]')
		for state in state_list : 
			url = state.xpath('.//a/@href').extract_first()
			state_link = self.domain + url
			if len(url.split('/')) == 1:
				yield scrapy.Request(url=state_link, callback=self.parse_city)	
			elif len(url.split('/')) == 2:				
				yield scrapy.Request(url=state_link, callback=self.parse_store)
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_detail)
			

	def parse_city(self, response):
		city_list = response.xpath('//ul[@class="c-directory-list-content"]//li[@class="c-directory-list-content-item"]')	
		for city in city_list :
			url = city.xpath('.//a/@href').extract_first()
			city_link = self.domain + url
			if len(url.split('/')) == 2:
				yield scrapy.Request(url=city_link, callback=self.parse_store)	
			else:				
				yield scrapy.Request(url=city_link, callback=self.parse_detail)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="c-location-grid-item"]')
		for store in store_list:
			url = store.xpath('.//h5//a/@href').extract_first()
			detail_link = self.domain + url[3:]
			yield scrapy.Request(url=detail_link, callback=self.parse_detail)	

	def parse_detail(self, response):
		print('~~~~~~~~~~~~~~~~~~~~~~', response.url)
		detail = response.xpath('//div[@class="information-nap"]')
		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//div[@class="banner-text"]//h1[@class="location-title"]//span[2]/text()'))
		item['store_number'] = ''
		item['address'] = self.validate(detail.xpath('.//span[@class="c-address-street-1"]/text()'))
		item['city'] = self.validate(detail.xpath('.//span[@itemprop="addressLocality"]/text()'))
		item['state'] = self.validate(detail.xpath('.//abbr[@class="c-address-state"]/text()'))
		item['zip_code'] = self.validate(detail.xpath('.//span[@class="c-address-postal-code"]/text()'))
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail.xpath('.//div[@class="c-phone-number c-phone-main-number"]//a/text()'))
		item['latitude'] = self.validate(detail.xpath('.//span[@class="coordinates"]//meta[@itemprop="latitude"]/@content'))
		item['longitude'] = self.validate(detail.xpath('.//span[@class="coordinates"]//meta[@itemprop="longitude"]/@content'))
		h_temp = ''
		hour_list = detail.xpath('.//table[@class="c-location-hours-details"]//tr')
		for hour in hour_list:
			h_temp = h_temp + self.validate(hour.xpath('.//td[1]/text()'))
			time_list = hour.xpath('.//td[2]//span')
			for time in time_list:
				h_temp += ' '+self.validate(time.xpath('./text()'))
			h_temp += ', '				
		item['store_hours'] = h_temp[2:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''