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

class carvel(scrapy.Spider):
	name = 'carvel'
	domain = 'www.carvel.com'
	history = ['']

	def start_requests(self):
		init_url  = 'https://locations.carvel.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="map-list-item-wrap is-single"]')
		for state in state_list : 
			state_link = state.xpath('.//a/@href').extract_first()
			# https://locations.carvel.com/pr/
			yield scrapy.Request(url=state_link, callback=self.parse_city)

	def parse_city(self, response):
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, sdch, br',
			'Referer':response.url,
			'Upgrade-Insecure-Requests':'1'
			}
		city_list = response.xpath('//div[@class="map-list-item-wrap is-single"]')	
		for city in city_list :
			city_link = city.xpath('.//a/@href').extract_first()
			yield scrapy.Request(url=city_link, headers=header, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="map-list-item-wrap js-map-list-item"]')
		for store in store_list:
			print('---------------------')
			detail = store.xpath('.//div[@class="map-list-item"]')
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('.//div[@class="loc-name"]//a/text()'))
			item['store_number'] = ''
			item['address'] = self.validate(detail.xpath('.//div[@class="address"]//div[@class="address-1"]/text()'))
			address = self.validate(detail.xpath('.//div[@class="address"]//div[@class="csz"]/text()'))
			item['city'] = address.split(',')[0].split()
			item['state'] = address.split(',')[1].strip().split(' ')[0]
			item['zip_code'] = address.split(',')[1].strip().split(' ')[1]
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail.xpath('.//div[@class="phone"]//a/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = detail.xpath('.//div[@class="defaultHours"]//div[@class="day-hour-row"]')
			for hour in hour_list:
				h_temp = h_temp + self.validate(hour.xpath('.//span[@class="daypart"]/text()')) + self.validate(hour.xpath('.//span[@class="time"]//span[@class="time-open"]/text()'))+ ' - '+ self.validate(hour.xpath('.//span[@class="time"]//span[@class="time-close"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''