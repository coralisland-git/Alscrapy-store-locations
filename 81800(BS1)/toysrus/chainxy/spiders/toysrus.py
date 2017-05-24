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

class toysrus(scrapy.Spider):
	name = 'toysrus'
	domain = 'www.toysrus.com'
	history = ['']

	def start_requests(self):
		init_url  = 'http://stores.toysrus.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="map-list-item-wrap"]')
		for state in state_list : 
			state_link = state.xpath('.//div[@class="map-list-item"]//a/@href').extract_first()
			yield scrapy.Request(url=state_link, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="map-list-item-wrap"]')	
		for city in city_list :
			city_link = city.xpath('.//div[@class="map-list-item"]//a/@href').extract_first()
			yield scrapy.Request(url=city_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="tlsmap_list"]//div[@class="map-list-item-wrap"]')
		for store in store_list:
			store_link = store.xpath('.//div[@class="address"]//header//a/@href').extract_first()
			yield scrapy.Request(url=store_link, callback=self.parse_detail)

	def parse_detail(self, response):
		detail = response.xpath('//div[@class="store-details"]')
		item = ChainItem()
		item['store_name'] = detail.xpath('.//div[@class="header"]//a[2]/text()').extract_first().split('[')[0].strip()
		item['store_number'] = detail.xpath('.//div[@class="header"]//a[2]/text()').extract_first().split('[')[1].strip()[:-1]
		address = detail.xpath('.//div[@class="address"]')
		item['address'] = address.xpath('.//span[1]//text()').extract_first().strip()
		try:
			item['address2'] = address.xpath('.//span[2]//text()').extract_first().strip()
		except:
			item['address2'] = ''
		item['city'] = address.xpath('.//span[3]//text()').extract_first().split(',')[0].split()
		item['state'] = address.xpath('.//span[3]//text()').extract_first().split(',')[1].strip().split(' ')[0]
		item['zip_code'] = address.xpath('.//span[3]//text()').extract_first().split(',')[1].strip().split(' ')[1]
		item['country'] = 'United States'
		item['phone_number'] = address.xpath('.//span[4]//text()').extract_first()
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = detail.xpath('.//div[@class="hoursCondensed"]//div[@class="day-hour-row"]')
		for hour in hour_list:
			h_temp = h_temp + hour.xpath('.//span[@class="daypart"]/text()').extract_first().strip() + hour.xpath('.//span[@class="time"]//span[@class="time-open"]/text()').extract_first().strip() + ' - '+ hour.xpath('.//span[@class="time"]//span[@class="time-close"]/text()').extract_first().strip() + ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		if item['store_name']+str(item['store_number']) not in self.history:
			yield item
			self.history.append(item['store_name']+str(item['store_number']))
