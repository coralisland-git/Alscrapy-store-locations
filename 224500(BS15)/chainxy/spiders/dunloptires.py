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
import pdb

class dunloptires(scrapy.Spider):
	name = 'dunloptires'
	domain = 'http://www.dunloptires.com'
	history = []
	
	def start_requests(self):
		init_url  = 'http://www.dunloptires.com/en-US/services/find-a-tire-store'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="states-list"]//a/@href').extract()
		for state in state_list : 
			state = self.domain + state
			yield scrapy.Request(url=state, callback=self.parse_city)	

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="cities-list"]//a/@href').extract()
		for city in city_list :
			city = self.domain + city
			yield scrapy.Request(url=city, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="all-stores"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="retailer-details"]//h4//text()').extract()[0])
			address = self.eliminate_space(response.xpath('//div[@class="retailer-details"]/p//text()').extract())[0]
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['phone_number'] = self.eliminate_space(response.xpath('//div[@class="retailer-details"]/p//text()').extract())[1]
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//ul[@class="hours-results"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if len(hour_list) < 10:
				item['store_hours'] = ''	
			yield item		
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'hours' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp