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

class express(scrapy.Spider):
	name = 'express'
	domain = 'https://stores.express.com/'
	domain2 = 'https://stores.expressfactoryoutlet.com/'
	history = ['']

	def start_requests(self):
		urls = ['https://stores.express.com/us', 'https://stores.express.com/pr/pr', 'https://stores.expressfactoryoutlet.com/us']
		yield scrapy.Request(url=urls[0], callback=self.parse_state, meta={'param':'main'}) 
		yield scrapy.Request(url=urls[1], callback=self.parse_city, meta={'param':'main'}) 
		yield scrapy.Request(url=urls[2], callback=self.parse_state, meta={'param':'outlet'}) 

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="c-directory-list-content-item"]')
		for state in state_list : 
			go_url = state.xpath('.//a/@href').extract_first()
			if response.meta['param'] == 'outlet':
				state_link = self.domain2 + go_url
			else:
				state_link = self.domain + go_url
			if len(go_url.split('/')) == 2 :
				yield scrapy.Request(url=state_link, callback=self.parse_city, meta={'param':response.meta['param']})
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_detail, meta={'param':response.meta['param']})

	def parse_city(self, response):
		city_list = response.xpath('//li[@class="c-directory-list-content-item"]')	
		for city in city_list :
			go_url = city.xpath('.//a/@href').extract_first()
			if response.meta['param'] == 'outlet':
				city_link = self.domain2 + go_url[3:]
			else:
				city_link = self.domain + go_url[3:]
			if len(go_url.split('/')) == 5 :
				yield scrapy.Request(url=city_link, callback=self.parse_detail, meta={'param':response.meta['param']})
			else :
				yield scrapy.Request(url=city_link, callback=self.parse_store, meta={'param':response.meta['param']})
	
	def parse_store(self, response):

		store_list = response.xpath('//div[@class="location-tile-subheader"]//a')
		for store in store_list:
			if response.meta['param'] == 'outlet':
				store_link = self.domain2 + store.xpath('./@href').extract_first()[6:]
			else:
				store_link = self.domain + store.xpath('./@href').extract_first()[6:]
			yield scrapy.Request(url=store_link, callback=self.parse_detail)

	def parse_detail(self, response):
		detail = response.xpath('//section[@class="location-info-section"]')
		item = ChainItem()
		item['store_name'] = detail.xpath('.//h1[@class="location-info-header"]//span[@class="geomodifier"]/text()').extract_first().strip()
		item['store_number'] = ''
		item['address'] = detail.xpath('.//address[@class="c-address"]//span[@class="c-address-street-1"]/text()').extract_first().strip()
		item['address2'] = ''
		item['city'] = detail.xpath('.//address[@class="c-address"]//span[@class="c-address-city"]//span[1]/text()').extract_first().strip()
		item['state'] = detail.xpath('.//address[@class="c-address"]//span[@class="c-address-state"]/text()').extract_first().strip()
		item['zip_code'] = detail.xpath('.//address[@class="c-address"]//span[@class="c-address-postal-code"]/text()').extract_first().strip()
		item['country'] = detail.xpath('.//address[@class="c-address"]//abbr/text()').extract_first().strip()
		item['phone_number'] = detail.xpath('.//div[@class="c-phone-number c-phone-main-number"]//a/text()').extract_first().strip()
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = detail.xpath('.//table[@class="c-location-hours-details"]//tbody//tr')
		for hour in hour_list : 
			weekday = hour.xpath('.//td[@class="c-location-hours-details-row-day"]/text()').extract_first()
			weektime = ''
			weektime_list = hour.xpath('.//td[@class="c-location-hours-details-row-intervals"]//div//span')
			if len(weektime_list) == 3:
				for time in weektime_list : 
					weektime = weektime + time.xpath('./text()').extract_first()
			h_temp = h_temp + weekday + weektime + ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		if item['store_name']+str(item['store_number']) not in self.history:
			yield item
			self.history.append(item['store_name']+str(item['store_number']))
