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

class learningexpresstoys(scrapy.Spider):
	name = 'learningexpresstoys'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://learningexpress.com/stores/locations.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//marker')
		for store in store_list:
			url = self.validate(store.xpath('./@web').extract_first())
			request = scrapy.Request(url=url, callback=self.parse_page)
			request.meta['store_name'] = self.validate(store.xpath('./@name').extract_first())
			request.meta['address'] = self.validate(store.xpath('./@address').extract_first())
			request.meta['address2'] = self.validate(store.xpath('./@address2').extract_first())
			request.meta['city'] = self.validate(store.xpath('./@city').extract_first())
			request.meta['state'] = self.validate(store.xpath('./@state').extract_first())
			request.meta['zip_code'] = self.validate(store.xpath('./@postal').extract_first())
			request.meta['latitude'] = self.validate(store.xpath('./@lat').extract_first())
			request.meta['longitude'] = self.validate(store.xpath('./@lng').extract_first())
			request.meta['phone_number'] = self.validate(store.xpath('./@phone').extract_first())
			request.meta['country'] = self.validate(store.xpath('./@country').extract_first())
			yield request

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			item['address'] = response.meta['address']
			item['address2'] = response.meta['address2']
			item['city'] = response.meta['city']
			item['state'] = response.meta['state']
			item['zip_code'] = response.meta['zip_code']
			item['country'] = response.meta['country']
			item['phone_number'] = response.meta['phone_number']
			item['latitude'] = response.meta['latitude']
			item['longitude'] =response.meta['longitude']
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="block_contact_text"]//text()').extract())
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
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
