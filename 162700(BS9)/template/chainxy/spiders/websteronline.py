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

class websteronline(scrapy.Spider):
	name = 'websteronline'
	domain = 'http://www.usbanklocations.com/'
	history = []

	def start_requests(self):
		init_url = 'http://www.usbanklocations.com/webster-bank-locations.htm?sb=name'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list_one = response.xpath('//div[contains(@class, "plb")]')
		store_list_two = response.xpath('//div[contains(@class, "plw")]')
		store_list = store_list_one + store_list_two
		for store in store_list:
			url = self.domain[:-1] + store.xpath('.//b//a/@href').extract_first()
			request = scrapy.Request(url=url, callback=self.parse_page)
			detail = self.eliminate_space(store.xpath('./text()').extract())
			request.meta['store_name'] = store.xpath('.//b//a/text()').extract_first()
			address = detail[1] + detail[2]
			request.meta['address'] = ''
			request.meta['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					request.meta['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					request.meta['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					request.meta['zip_code'] = temp[0].replace(',','')
				else:
					request.meta['address'] += temp[0].replace(',', '') + ' '
			yield request

		pagenation = response.xpath('//div[contains(@class, "panelpn")]//a')
		pagenation = pagenation[len(pagenation)-1].xpath('./@href').extract_first()
		if pagenation is not None:
			pagenation = self.domain + pagenation
			yield scrapy.Request(url=pagenation, callback=self.body)

	def parse_page(self, response):
		phone = response.xpath('//td[@property="v:tel"]/text()').extract_first()
		item = ChainItem()
		item['store_name'] = response.meta['store_name']
		item['address'] = response.meta['address']
		item['city'] = response.meta['city']
		item['state'] = response.meta['state']
		item['zip_code'] = response.meta['zip_code']
		item['country'] = 'United States'
		item['phone_number'] = self.validate(phone)
		yield item			


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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''