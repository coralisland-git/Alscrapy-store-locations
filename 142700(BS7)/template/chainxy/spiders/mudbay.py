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

class mudbay(scrapy.Spider):
	name = 'mudbay'
	domain = 'http://mudbay.com'
	history = []

	def start_requests(self):
		init_url = 'http://mudbay.com/store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = etree.HTML(response.xpath('//script[@id="all-locations"]/text()').extract()[0]).xpath('//address//@href')
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):

		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//h1/text()').extract_first())
		address = self.eliminate_space(response.xpath('//address//text()').extract())
		item['address'] = address[0]
		addr = address[1].split(',')
		item['city'] = self.validate(addr[0].strip())
		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
		item['country'] = 'United States'
		try:
			item['phone_number'] = address[2]
		except:
			pass
		h_temp = ''
		hour_list = self.eliminate_space(response.xpath('//p[1]//text()').extract())
		for hour in hour_list:
			if '-' in hour:
				h_temp += hour +', '
		item['store_hours'] = h_temp[:-2]
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