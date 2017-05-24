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

class bojangles(scrapy.Spider):
	name = 'bojangles'
	domain = 'http://locations.bojangles.com/'
	history = ['']

	def start_requests(self):
		init_url  = 'http://locations.bojangles.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="c-directory-list-content-item"]')
		for state in state_list : 
			state_link = self.domain + state.xpath('.//a/@href').extract_first()
			if len(state_link) > 10 :
				yield scrapy.Request(url=state_link, callback=self.parse_city)
			else :
				yield scrapy.Request(url=state_link, callback=self.parse_store)

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="c-directory-list-content-item"]')	
		for city in city_list :
			city_link = self.domain + city.xpath('.//a/@href').extract_first()
			yield scrapy.Request(url=city_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="location"]')
		if len(store_list) == 0 :
			store = response.xpath('//div[@class="main-row"]')
			item = ChainItem()
			item['store_name'] = store.xpath('.//h1[@class="c-location-title"]/text()').extract_first().split(',')[0]
			item['store_number'] = store.xpath('.//div[@class="restaurant-number"]/text()').extract_first().split(' ')[1].strip()[1:]
			item['address'] = store.xpath('.//div[@class="c-address"]//span[@class="c-address-street c-address-street-1"]/text()').extract_first()
			item['address2'] = ''
			item['city'] = store.xpath('.//div[@class="c-address"]//span[@class="c-address-city"]//span/text()').extract_first()
			item['state'] = store.xpath('.//div[@class="c-address"]//span[@class="c-address-state"]/text()').extract_first()
			item['zip_code'] = store.xpath('.//div[@class="c-address"]//span[@class="c-address-postal-code"]/text()').extract_first()
			item['country'] = 'United States'
			item['phone_number'] = store.xpath('.//span[@class="c-phone-number-span c-phone-main-number-span"]/text()').extract_first()
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//table[@class="c-location-hours-details"]//tbody//tr')
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
			yield item
		else :
			for store in store_list	:
				item = ChainItem()
				item['store_name'] = store.xpath('.//h4[@class="location-title"]//a/text()').extract_first().split(',')[0]
				item['store_number'] = store.xpath('.//div[@class="location-info-number"]/text()').extract_first().split(' ')[1].strip()[1:]
				item['address'] = store.xpath('.//div[@class="location-info-address"]//span[@class="c-address-street c-address-street-1"]/text()').extract_first()
				item['address2'] = ''
				item['city'] = store.xpath('.//div[@class="location-info-address"]//span[@class="c-address-city"]//span/text()').extract_first()
				item['state'] = store.xpath('.//div[@class="location-info-address"]//span[@class="c-address-state"]/text()').extract_first()
				item['zip_code'] = store.xpath('.//div[@class="location-info-address"]//span[@class="c-address-postal-code"]/text()').extract_first()
				item['country'] = 'United States'
				item['phone_number'] = store.xpath('.//div[@class="location-info-phone"]//a/text()').extract_first()
				item['latitude'] = ''
				item['longitude'] = ''
				h_temp = ''
				hour_list = store.xpath('.//table[@class="c-location-hours-details"]//tbody//tr')
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
				yield item

		