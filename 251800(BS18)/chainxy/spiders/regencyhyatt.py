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

class regencyhyatt(scrapy.Spider):
	name = 'regencyhyatt'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://regency.hyatt.com/content/brandredesign/en/hyattregency/locations/jcr:content/parsys/maps.hregencyjsonformat.html'
		header = {
			"accept":"application/json, text/javascript, */*; q=0.01",
			"accept-encoding":"gzip, deflate, br",
			"x-requested-with":"XMLHttpRequest"
		}
		yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		try:
			store_list = json.loads(response.body)['HOTELS']
			for con_name, continent in store_list.items():
				for cou_name, country in continent.items():
					if 'NotAvailable' in country:
						for sto_name, store in country['NotAvailable'].items():
							try:
								item = ChainItem()
								item['store_name'] = self.validate(store['HOTEL_NAME'])
								item['country'] = self.validate(store['HOTEL_COUNTRY'])
								item['latitude'] = self.validate(store['LATITUDE'])
								item['longitude'] = self.validate(store['LONGITUDE'])
								link = self.validate(store['HOTEL_URL'])
								yield scrapy.Request(url=link,  callback=self.parse_page, meta={'item':item})
							except:
								pass
					else:
						for sta_name, state in country.items():
							for sto_name, store in state.items():
								try:
									item = ChainItem()
									item['store_name'] = self.validate(store['HOTEL_NAME'])
									item['country'] = self.validate(store['HOTEL_COUNTRY'])
									item['latitude'] = self.validate(store['LATITUDE'])
									item['longitude'] = self.validate(store['LONGITUDE'])
									link = self.validate(store['HOTEL_URL'])
									yield scrapy.Request(url=link,  callback=self.parse_page, meta={'item':item})
								except:
									pass
		except:
			pass					

	def parse_page(self, response):
		try:
			item = response.meta['item']
			detail = self.eliminate_space(response.xpath('//div[@class="addresspanel"]//p[@class="address"]//text()').extract())
			item['address'] = detail[0]
			item['city'] = detail[1].split(',')[0]
			try:
				item['state'] = detail[1].split(',')[1]
			except:
				pass
			try:
				item['zip_code'] = detail[3]
			except:
				pass
			item['phone_number'] = self.validate(response.xpath('//div[@class="addresspanel"]//p[@class="phnNo"]/text()').extract_first())
			if ':' in item['phone_number']:
				item['phone_number'] = item['phone_number'].split(':')[1].strip()
			yield item
		except:
			pass


	def validate(self, item):
		try:
			return item.strip().replace('\xa0','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != ',':
				tmp.append(self.validate(item))
		return tmp