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
import unicodedata

class eatpdq(scrapy.Spider):
	name = 'eatpdq'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.eatpdq.com/locations/find-a-location'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="locations-by-state"]//li//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = response.xpath('//div[@class="location-inner"]')
			item = ChainItem()
			h_temp = self.validate(detail.xpath('//div[@class="name"]//h1/text()').extract_first())
			item['store_name'] = h_temp
			item['coming_soon'] = '0'
			if 'Coming Soon' in h_temp:
				item['store_name'] = h_temp.split('-')[0].strip()
				item['coming_soon'] = '1'
			address = detail.xpath('.//div[@class="address"]//text()').extract()
			item['address'] = self.validate(address[0])
			addr = address[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail.xpath('.//tel//a/text()').extract_first())
			h_temp = ''
			hour_list = detail.xpath('.//div[@class="hours"]//div//text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '':
					h_temp += self.validate(hour) + ' '
			item['store_hours'] = h_temp.strip().replace('For Catering: Click Here', '')
			yield item			
		except:
			pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''