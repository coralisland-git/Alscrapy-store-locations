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

class meineke_us(scrapy.Spider):
	name = 'meineke_us'
	domain = 'https://www.meineke.com'
	history = []
	
	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.meineke.com/locations/'
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
			address = self.str_concat(response.xpath('//div[@itemprop="address"]//text()').extract(), ' ')
			item['address'] = ''
			item['city'] = ''
			item['state'] = ''
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
			item['country'] = self.check_country(item['state'])
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
			pdb.set_trace()

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'directions' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '' and 'directions' not in self.validate(item).lower():
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'