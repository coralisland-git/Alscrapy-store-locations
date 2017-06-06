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

class tisol(scrapy.Spider):
	name = 'tisol'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://tisol.ca/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "et_pb_module et_pb_toggle")]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h5[@class="et_pb_toggle_title"]/text()').extract_first())	
				detail = self.eliminate_space(store.xpath('.//div[contains(@class, "et_pb_toggle_content")]/p[1]/text()').extract())
				addr_list = detail[0].split(',')
				item['address'] = self.validate(addr_list[0])
				item['city'] = self.validate(addr_list[1])
				item['zip_code'] = self.validate(addr_list[2])
				item['country'] = self.validate('Canada')
				item['phone_number'] = detail[1]
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//div[contains(@class, "et_pb_toggle_content")]/p[2]//text()').extract())
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
			return item.replace('\u2013', '').strip()
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
