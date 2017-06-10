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

class cartier(scrapy.Spider):
	name = 'cartier'
	domain = 'https://secure.www.cartier.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'https://secure.www.cartier.com/en-us/find-boutique/store-locator-listing.html'
		yield scrapy.Request(url=init_url, callback=self.parse_country) 

	def parse_country(self, response):
		country_list = response.xpath('//a[@class="more-button"]')
		for country in country_list:
			country_link = self.domain + country.xpath('./@href').extract_first()
			country_name = self.validate(country.xpath('./text()').extract_first())
			yield scrapy.Request(url=country_link, callback=self.parse_store, meta={'country':country_name})
	
	def parse_store(self, response):
		store_list = response.xpath('//a[@class="boutique-header-link"]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page, meta={'country':response.meta['country']})

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@itemprop="name"]/text()').extract_first())
			addr_list = self.eliminate_space(response.xpath('//span[@itemprop="address"]/text()').extract())
			a_temp = ''
			for addr in addr_list:
				a_temp += addr + ', '
			item['address'] = a_temp[:-2]
			item['city'] = self.validate(response.xpath('//span[@itemprop="city"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="state"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = response.meta['country']
			if item['country'] == 'United States':
				try:
					item['state'] = item['zip_code'].split(' ')[0]
					item['zip_code'] = item['zip_code'].split(' ')[1]
				except:
					pass
			item['phone_number'] = self.validate(response.xpath('//div[@class="boutique_details__con desktop-visible"]//div[@class="items clearfix"][1]//div[2]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//time[@itemprop="openingHours"]//text()').extract())
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = response.url
			yield item			
		except:
			pass

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp