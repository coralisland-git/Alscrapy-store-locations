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
import pdb

class stagestores(scrapy.Spider):
	name = 'stagestores'
	domain = 'http://stores.stage.com/'
	history = []

	def start_requests(self):
		init_url = 'http://stores.stage.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="c-directory-list-content-item"]//a[@class="c-directory-list-content-item-link"]/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			if len(state.split('/')) == 1:
				yield scrapy.Request(url=state_link, callback=self.parse_city)	
			elif len(state.split('/')) == 2:				
				yield scrapy.Request(url=state_link, callback=self.parse_store)
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_page)

	def parse_city(self, response):
		city_list = response.xpath('//li[@class="c-directory-list-content-item"]//a[@class="c-directory-list-content-item-link"]/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			if len(city.split('/')) == 2:
				yield scrapy.Request(url=city_link, callback=self.parse_store)
			else:
				yield scrapy.Request(url=city_link, callback=self.parse_page)
	
	def parse_store(self, response):
		store_list = response.xpath('//li[@class="location-card"]//a[contains(@class, "location-card-visit-link")]/@href').extract()
		for store in store_list:
			store_link = self.domain + store[3:]
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[@class="about-this-store-main-info"]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('//h1[@class="c-location-title"]/text()')).strip()
			item['store_number'] = ''
			item['address'] = self.validate(detail.xpath('.//span[@itemprop="streetAddress"]/text()'))
			item['address2'] = ''
			item['city'] = self.validate(detail.xpath('.//span[@itemprop="addressLocality"]/text()'))
			item['state'] = self.validate(detail.xpath('.//span[@itemprop="addressRegion"]/text()'))
			item['zip_code'] = self.validate(detail.xpath('.//span[@itemprop="postalCode"]/text()'))
			item['country'] = self.validate(detail.xpath('.//span[@itemprop="addressCountry"]/text()'))
			item['phone_number'] = self.validate(detail.xpath('.//span[@itemprop="telephone"]/text()'))
			h_temp = ''
			hour_list = detail.xpath('//tr[contains(@class, "c-location-hours-details-row")]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//td[@class="c-location-hours-details-row-day"]/text()')) + ' ' 
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-details-row-intervals-instance-open"]/text()')) + ' - '
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-details-row-intervals-instance-close"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''