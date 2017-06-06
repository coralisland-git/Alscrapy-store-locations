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

class tutoringclub(scrapy.Spider):
	name = 'tutoringclub'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.tutoringclub.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="addr_wrap"]//a[1]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "club-address-phone")]//text()').extract())
			address = ''
			for de in detail[1:-2]:
				address += de + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address[:-2])
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
			item['phone_number'] = self.validate(detail[-2])
			if '@' in item['phone_number'] : 
				item['phone_number'] = self.validate(detail[-1])
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[contains(@class, "club-hours")]//div[@class="textwidget"]//text()').extract())
			cnt = 1
			for hour in hour_list[1:]:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\t','').replace('\r','')
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