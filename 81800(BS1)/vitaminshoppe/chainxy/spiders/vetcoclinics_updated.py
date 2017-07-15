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

class vetcoclinics(scrapy.Spider):
	name = 'vetcoclinics'
	domain = 'https://www.vitaminshoppe.com'
	history = []

	def __init__(self, *args, **kwargs):
		init_url = 'https://www.vitaminshoppe.com/sl/storeLocator.jsp'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@class="results-right state-listing"]//a[@class="state-link"]/@href').extract()
		for state in state_list:
			state = self.domain + state
			yield scrapy.Request(url=state, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//a[@class="gray-link corisande-bold18"]/@href').extract()
		for city in city_list:
			city = self.domain + city
			yield scrapy.Request(url=city, callback=self.parse_store)

	def parse_store(self, response):
		detail = response.xpath('//div[@class="block shadow results"]')
		try:
			item = ChainItem()
			item['store_name'] = detail.xpath('.//span[@class="head"]/text()').extract_first()
			item['address'] = detail.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()
			item['city'] = detail.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()
			item['state'] = detail.xpath('.//span[@itemprop="addressRegion"]/text()').extract_first()
			item['zip_code'] = detail.xpath('.//span[@itemprop="postalCode"]/text()').extract_first()
			item['country'] = 'United States'

			item['phone_number'] = detail.xpath('.//a[contains(@class, "tel-no")]/text()').extract_first()
			if item['phone_number'] == None:
				item['phone_number'] = ''
			h_temp = ''
			hour_list = self.eliminate_space(detail.xpath('.//td[@itemprop="hoursAvailable"]/text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\xa0', ' ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
