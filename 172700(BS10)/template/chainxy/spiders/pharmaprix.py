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

class pharmaprix(scrapy.Spider):
	name = 'pharmaprix'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www1.pharmaprix.ca/en/Store-Locator/pharmacist-listing'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//li[contains(@class, "strloc-allstr-store-list-item")]//a[@class="strloc-allstr-store-link"]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="strloc-page-title"]/text()').extract_first())
			address = self.eliminate_space(response.xpath('//dd[@class="strloc-dtl-access-info-content block-content padding-bottom-block"][2]//text()').extract())
			item['address'] = self.validate(address[0])		
			item['city'] = self.validate(address[1][:-10])
			item['state'] = self.validate(address[1][-10:-8])
			item['zip_code'] = self.validate(address[1][-8:])
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(response.xpath('//dd[@class="strloc-dtl-access-info-content"][1]/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//li[@class="strloc-dtl-store-hours-list-item"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//span[1]/text()').extract_first()) + ' ' + self.validate(hour.xpath('.//span[2]/text()').extract_first()) + ', '
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