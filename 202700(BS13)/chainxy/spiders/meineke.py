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

class meineke(scrapy.Spider):
	name = 'meineke'
	domain = 'http://www.meineke.ca'
	history = []
	
	def start_requests(self):
		init_url  = 'http://www.meineke.ca/locations/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[contains(@class, "cities-states-page")]//ul[@class="list-unstyled"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_city)	
		
	def parse_city(self, response):
		city_list = response.xpath('//div[contains(@class, "cities-states-page")]//ul[@class="list-unstyled"]//a/@href').extract()
		for city in city_list :
			city_link = response.url + city
			yield scrapy.Request(url=city_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//a[@class="light-grey-button more-details"]/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@itemprop="name"]//span[1]/text()').extract_first()) + '-' + self.validate(response.xpath('//h1[@itemprop="name"]//span[2]/text()').extract_first())
			item['store_number'] = self.validate(response.xpath('//h1[@itemprop="name"]//span[3]/text()').extract_first())[1:]
			addr_list = self.eliminate_space(response.xpath('//div[@itemprop="address"]//text()').extract())
			address = ''
			if len(addr_list) == 2:
				item['address'] = addr_list[0]
				address = addr_list[1].split(',')
			elif len(addr_list) == 3:
				item['address'] = addr_list[0] + ' ' + addr_list[1]
				address = addr_list[2].split(',')
			try:
				item['city'] = self.validate(address[0])
				item['state'] = self.validate(address[1])[:2].strip()
				item['zip_code'] = self.validate(address[1])[2:].strip()
			except:
				pass
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(response.xpath('//p[@itemprop="telephone"]//a/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@itemprop="openingHours"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pass

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'directions' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''