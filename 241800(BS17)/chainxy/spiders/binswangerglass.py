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

class binswangerglass(scrapy.Spider):
	name = 'binswangerglass'
	domain = 'http://www.binswangerglass.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.binswangerglass.com/contact-us/find-a-location'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="locations clear"]')
		for store in store_list:
			link = store.xpath('.//h3/a/@href').extract_first()
			if link:
				link = self.domain + link
				yield scrapy.Request(url=link, callback=self.parse_page)
			else:
				item = ChainItem()
				item['store_name'] = store.xpath('.//h3/text()').extract_first()
				address = store.xpath('.//p[@class="address"]/text()').extract_first()
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
				item['phone_number'] = store.xpath('.//p[@class="phone"]//a/text()').extract_first()
				yield item
 
	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@id="location-name"]//h1/text()').extract_first())
			if '-' in item['store_name']:
				item['store_name'] = item['store_name'].split('-')[0].strip()
			address = self.str_concat(response.xpath('//div[@class="location-info-contact-address clear"]//text()').extract(), ', ')
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
			item['phone_number'] = self.validate(response.xpath('//span[@class="phone bold blue"]//a/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="location-info-contact-hours"]//text()').extract())
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