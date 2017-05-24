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

class sallybeauty(scrapy.Spider):
	name = 'sallybeauty'
	domain = 'http://www.sallybeauty.com/'
	history = []

	def start_requests(self):
		
		init_url = 'https://stores.sallybeauty.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="rio-listItem"]//a[@class="gaq-link"]/@href').extract()
		for state in state_list : 
			yield scrapy.Request(url=state, callback=self.parse_city)	

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="rio-listItem"]//a[@class="gaq-link"]/@href').extract()
		for city in city_list :
			yield scrapy.Request(url=city, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="rio-list-links"]//a[contains(@data-gaq, "View Details")]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[@id="rio-store-details"]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('.//div[@id="rio-store-name"]/text()')).split('#')[0].strip()
			item['store_number'] = self.validate(detail.xpath('.//div[@id="rio-store-name"]/text()')).split('#')[1].strip()
			item['address'] = self.validate(detail.xpath('.//div[@id="rio-address-section"]//span/text()'))
			# pdb.set_trace()
			item['address2'] = ''
			address = detail.xpath('.//div[@id="rio-address-section"]/text()').extract()[1].strip()
			item['city'] = address.split(',')[0].strip()
			item['state'] = address.split(',')[1].strip().split(' ')[0].strip()
			item['zip_code'] = address.split(',')[1].strip().split(' ')[1].strip()
			item['country'] = ''
			try:
				count = int(item['zip_code'])
				if item['state'] == 'PR':
					item['country'] = 'Puert Rico'
				else :
					item['country'] = 'United States'
			except :
				item['country'] = 'Canada'
				
			item['phone_number'] = self.validate(detail.xpath('.//div[@id="rio-store-phone"]/text()'))
			h_temp = ''
			hour_list = detail.xpath('//div[@class="day-hour-row"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//div[@class="daypart"]/text()')) + ' ' + self.validate(hour.xpath('.//div[@class="hours"]/text()')) + ', '
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