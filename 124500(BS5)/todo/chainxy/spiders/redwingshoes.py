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

class redwingshoes(scrapy.Spider):
	name = 'redwingshoes'
	domain = 'http://stores.redwing.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'http://stores.redwing.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_country) 

	def parse_country(self, response):
		country_list = response.xpath('//li[@class="directory-index-item"]//a/@href').extract()
		for country in country_list:
			country_url = self.domain + country
			yield scrapy.Request(url=country_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//li[@class="directory-index-item"]//a/@href').extract()
		for state in state_list : 
			state_url = self.domain + state
			yield scrapy.Request(url=state_url, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//li[@class="directory-index-item"]//a/@href').extract()
		for city in city_list :
			city_url = self.domain + city
			yield scrapy.Request(url=city_url, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="listing"]')
		for store in store_list:
			store_url = self.domain + store.xpath('.//a[contains(@class, "website")]/@href').extract_first()
			request = scrapy.Request(url=store_url, callback=self.parse_page)
			request.meta['store_name'] = self.validate(store.xpath('.//a//h3/text()'))
			address = self.validate(store.xpath('.//div[@class="address"]/text()[2]')).split(',')
			request.meta['address'] = self.validate(store.xpath('.//div[@class="address"]/text()[1]'))
			request.meta['city'] = address[0].strip()
			request.meta['state'] = address[1].strip()
			request.meta['country'] = self.country(response.url)
			request.meta['zip_code'] = address[2].strip()
			request.meta['phone_number'] = self.validate(store.xpath('.//span[@class="directory-phone"]/text()'))
			yield request

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			item['address'] = response.meta['address']
			item['city'] = response.meta['city']
			item['state'] = response.meta['state']
			item['zip_code'] = response.meta['zip_code']
			item['country'] = response.meta['country']
			item['phone_number'] = response.meta['phone_number']
			h_temp = ''
			hour_list = response.xpath('//div[@class="hops"]//div[@class="hop"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//div[@class="hop-day"]/text()')) + ' ' + self.validate(hour.xpath('.//div[@class="hop-hours-open"]/text()')) 
				h_temp += '-' + self.validate(hour.xpath('.//div[@class="hop-hours-close"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pdb.set_trace()

	def country(self, item):
		temp = item.split('/')
		return temp[3].upper()

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''