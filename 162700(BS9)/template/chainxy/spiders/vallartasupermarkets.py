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

class vallartasupermarkets(scrapy.Spider):
	name = 'vallartasupermarkets'
	domain = 'http://www.vallartasupermarkets.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.vallartasupermarkets.com/en/store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store storeListing"]/a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//div[@class="store columnMiddle1"]//h1/text()').extract_first())
		address_list = self.eliminate_space(response.xpath('//div[@class="store columnMiddle1"]//p[1]/text()').extract())
		a_temp = ''
		for address in address_list:
			a_temp += address + ', '
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(a_temp)
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += temp[0].replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] = temp[0]
			elif temp[1] == 'ZipCode':
				item['zip_code'] = temp[0].replace(',','')
			else:
				item['address'] += temp[0].replace(',', '') + ' '
		item['country'] = 'United States'
		phone_list = self.eliminate_space(response.xpath('//div[@class="store columnMiddle1"]//p[2]/text()').extract())
		p_temp = ''
		for phone in phone_list:
			if ':' in phone:
				p_temp += self.validate(phone.split(':')[1]) + ', '
		item['phone_number'] = self.validate(p_temp[:-2])
		h_temp = ''
		hour_list = ''
		for hour in hour_list:
			h_temp += hour + ', '
		item['store_hours'] = self.validate(response.xpath('//div[@class="store columnMiddle1"]//p[3]/text()').extract_first())
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
