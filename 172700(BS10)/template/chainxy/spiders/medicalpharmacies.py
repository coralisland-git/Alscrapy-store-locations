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

class medicalpharmacies(scrapy.Spider):
	name = 'medicalpharmacies'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.medicalpharmacies.com/store-locator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="content"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.detail)

	def detail(self, response):
		try:
			item = ChainItem()
			detail = response.xpath('//div[@id="content-two"]')
			item['store_name'] = self.validate(detail.xpath('.//h4[1]/text()').extract_first())
			address = self.eliminate_space(detail.xpath('.//p[1]//text()').extract())
			if len(address) == 2:
				item['address'] = address[0]
				addr = address[1].split(',')
			elif len(address) == 3:
				item['address'] = address[0] + ', ' + address[1]
				addr = address[2].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1])[:2]
			item['zip_code'] = self.validate(addr[1])[2:]
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(detail.xpath('.//table//tr//td[2]/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//div[@id="twocolumns"]//table//tr')
			for hour in hour_list:
				if self.validate(hour.xpath('.//td[1]/text()').extract_first()) != '':
					h_temp += self.validate(hour.xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour.xpath('.//td[2]/text()').extract_first()) + ', '
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

