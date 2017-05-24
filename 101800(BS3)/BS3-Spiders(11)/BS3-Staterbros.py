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

class BS3Saterbros(scrapy.Spider):
	name = 'BS3-Staterbros'
	domain = 'https://www.staterbros.com/'
	history = []

	def start_requests(self):
		
		init_url  = 'http://www.staterbros.com/store-locator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		store_list = response.xpath('//div[@class="store-wrapper"]//div[@class="store"]')
		# print('~~~~~~~~~~~~~~~~~~~~~~~~~', len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="title"]/text()')) + ' ' + self.validate(store.xpath('.//div[@class="name"]/text()'))
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//div[@class="address"]//p[1]/text()'))
			address = self.validate(store.xpath('.//div[@class="address"]//p[2]/text()'))
			item['address2'] = ''
			item['city'] = address.split(',')[0].strip()
			item['state'] = address.split(',')[1].strip().split(' ')[0].strip()
			if len(item['state']) > 2:
				temp = item['state']
				item['state'] = item['city']
				item['city'] = temp
			item['zip_code'] = address.split(',')[1].strip().split(' ')[1].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]//p[2]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//div[@class="hours"]//p')
			for hour in hour_list:
				if self.validate(hour.xpath('.//strong/text()')) == '':
					h_temp += self.validate(hour.xpath('./text()')) + ' '
				else :
					h_temp += self.validate(hour.xpath('.//strong/text()')) + ' '
			item['store_hours'] = h_temp.strip()
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''