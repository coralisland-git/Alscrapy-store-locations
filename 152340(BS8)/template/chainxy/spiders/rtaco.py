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

class rtaco(scrapy.Spider):
	name = 'rtaco'
	domain = 'http://www.rtacos.com/'
	history = []

	def start_requests(self):
		init_url = 'http://www.rtacos.com/rtaco-store-locator.html'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = self.eliminate_space(response.xpath('//select//option/@value').extract())
		for store in store_list:
			store = self.domain + store[6:]	
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		detail = self.eliminate_space(response.xpath('//h1[@class="location"]//text()').extract())
		if len(detail) != 0:
			try:
				item['phone_number'] = ''
				if len(detail) == 3:
					item['store_name'] = detail[0]
					address = detail[1]
					item['phone_number'] = detail[2]
					if '303' in detail[1]:
						address = detail[2]
						item['phone_number'] = detail[1]

				elif len(detail) == 2:
					item['store_name'] = detail[0]
					if '(' in item['store_name'] :
						item['phone_number'] = '(' + item['store_name'].split('(')[1]
						item['store_name'] = item['store_name'].split('(')[0]						
					address = detail[1]
					if '(' in address:
						item['phone_number'] = '(' + address.split('(')[1]
					if ':' in address:
						item['phone_number'] = address.split(':')[1]

				if 'Phone:' in item['phone_number']:
					item['phone_number'] = self.validate(item['phone_number'].split(':')[1])
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0]
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0]
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = 'United States'
				h_temp =''
				hour_list = self.eliminate_space(response.xpath('//div[@id="container"]//p//text()').extract())
				for hour in hour_list:
					if ':' in hour and '-' in hour:
						h_temp += self.validate(hour) + ', '
				item['store_hours'] = h_temp[:-2]
				if item['store_hours'] == '':
					item['coming_soon'] = '1'
				else:
					item['coming_soon'] = '0'
				yield item			
			except:
				pass

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '').replace('\u2022', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'Coming Soon' not in self.validate(item) and 'Open' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp