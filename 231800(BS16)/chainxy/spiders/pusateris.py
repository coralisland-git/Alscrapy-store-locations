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

class pusateris(scrapy.Spider):
	name = 'pusateris'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.pusateris.com/pages/contact-us'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="grid__item large--one-half"]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['store_name'] = detail[0]
				item['address'] = detail[1]
				item['city'] = detail[2].split(',')[0].strip()
				item['state'] = detail[2].split(',')[1].strip()
				item['zip_code'] = detail[3]
				item['country'] = 'Canada'
				item['phone_number'] = detail[4]
				h_temp = ''
				cnt = 0
				for ind in range(5, len(detail)):
					h_temp += detail[ind]
					if cnt % 2 == 1:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('\u2014','-')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp