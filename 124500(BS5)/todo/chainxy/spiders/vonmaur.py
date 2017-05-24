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
import pdb

class vonmaur(scrapy.Spider):
	name = 'vonmaur'
	domain = 'http://www.vonmaur.com/'
	history = []

	def start_requests(self):
		init_url = 'http://www.vonmaur.com/Stores.aspx'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="divStoresListStore"]//a/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):

		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//div[@class="divStoresTitle"]/text()').extract_first())
		item['address'] = self.validate(response.xpath('//div[@class="divStoreInfoBox"]//div[1]/text()').extract_first())
		addr = self.validate(response.xpath('//div[@class="divStoreInfoBox"]//div[2]/text()').extract_first()).split(',')
		# pdb.set_trace()
		item['city'] = addr[0].strip()
		item['state'] = addr[1].strip().split(' ')[0].strip()
		item['zip_code'] = addr[1].strip().split(' ')[1].strip()
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//div[@class="divStoreInfoBox"]//div[3]/text()').extract_first())
		h_temp = ''
		hour_list = response.xpath('//div[@class="divStoreInfoBoxHours"]//text()').extract()
		for hour in hour_list:
			if hour.strip() != 'STORE HOURS':
				h_temp += self.validate(hour) + ', '
		item['store_hours'] = h_temp[:-2]
		yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''