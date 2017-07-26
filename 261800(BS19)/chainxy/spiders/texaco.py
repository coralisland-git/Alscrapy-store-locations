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

class texaco(scrapy.Spider):
	name = 'texaco'
	domain = 'https://www.localstore.net'
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		letter_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
		for letter in letter_list:
			init_url  = 'https://www.localstore.net/stores/737143/texaco/'+letter+'/'
			yield scrapy.Request(url=init_url, callback=self.parse_city) 

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="overviewlistlabel overviewlist overflow-ellipsis"]//a/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			yield scrapy.Request(url=city_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//tr[@class="search_inactive"]//td[3]//a/@href').extract()
		for store in store_list:
			if 'search' not in store:
				store_link = self.domain + store
				yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@itemprop="name"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "opentimes_box")]//text()').extract())
			item['phone_number'] = ''
			for de in detail:
				if '-' in de:
					item['phone_number'] = de
			yield item			
		except:
			pass

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''