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

class sunskisports(scrapy.Spider):
	name = 'sunskisports'
	domain = 'https://www.sunandski.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.sunandski.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@class="btn btn--sml"]/@href').extract()
		for store in store_list:
			store = self.domain	+ store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):

		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//div[@class="card__content"]//h1//text()').extract()[0])
		item['address'] = self.validate(response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first())
		item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
		item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
		item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
		h_temp = ''
		hour_list = self.eliminate_space(response.xpath('//div[@class="card__content-group"][2]//text()').extract())
		for hour in hour_list:
			if 'Hours' not in hour:
				h_temp += self.validate(hour)
				if ':' in hour:
					h_temp += ', '
				else:
					h_temp += ' '
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