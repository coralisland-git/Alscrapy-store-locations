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

class llbean(scrapy.Spider):
	name = 'llbean'
	domain = 'https://www.llbean.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.llbean.com/llb/shop/1000001703?nav=gn-'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@class, "listColumn")]//a/@href').extract()
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		store = response.xpath('//div[@class="location"]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//strong[@class="title"]//span/text()').extract_first())
			item['address'] = self.validate(store.xpath('.//span[@class="street-address"]/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//em[@class="locality"]/text()').extract_first())
			item['state'] = self.validate(store.xpath('.//abbr[@class="region"]/text()').extract_first())
			item['zip_code'] = self.validate(store.xpath('.//em[@class="postal-code"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//strong[@class="tel"]/text()').extract_first())
			item['latitude'] = self.validate(str(response.xpath('//meta[@itemprop="latitude"]/@content').extract_first()))
			item['longitude'] = self.validate(str(response.xpath('//meta[@itemprop="longitude"]/@content').extract_first()))
			h_temp = ''
			hour_list = self.eliminate_space(store.xpath('.//ul[@class="schedule hoursActive"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if item['address'] != '':
				yield item	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp