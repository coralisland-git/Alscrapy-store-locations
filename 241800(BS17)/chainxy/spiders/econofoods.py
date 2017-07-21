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

class econofoods(scrapy.Spider):
	name = 'econofoods'
	domain = 'http://www.econofoods.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.econofoods.com/store-location'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="state-result"]//div[contains(@class, "location")]//a[contains(@href, "/store-location/store-detail?store_name=")]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="store-locations"]//h1/text()').extract_first()).split('#')[0].strip()
			item['store_number'] = self.validate(response.xpath('//div[@class="store-locations"]//h1/text()').extract_first()).split('#')[1].strip()
			address = self.validate(response.xpath('//div[@class="store-locations"]//div[@class="address"]//p/text()').extract_first())
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
			detail = self.eliminate_space(response.xpath('//div[@class="store-locations"]//div[@class="store-info"]//text()').extract())
			for ind in range(0, len(detail)):
				if 'Phone' in detail[ind]:
					item['phone_number'] = self.validate(detail[ind+1])
					break
			h_temp = ''
			for ind in range(0, len(detail)):
				if 'day' in detail[ind].lower():
					h_temp += self.validate(detail[ind]) + ' ' + self.validate(detail[ind+1]) + ', '
					ind += 2
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass

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