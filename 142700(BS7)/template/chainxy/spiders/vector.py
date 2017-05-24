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
import unicodedata
import usaddress

class vector(scrapy.Spider):
	name = 'vector'
	domain = 'http://www.vetcor.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.vetcor.com/our-practices'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_links = response.xpath('//li[@class="drop"]//div//ul//li//a')
		for store_link in store_links:
			request_url = store_link.xpath('./@href').extract_first()
			request = scrapy.Request(url=request_url, callback=self.parse_store)
			request.meta['store'] = store_link.xpath('./text()').extract_first()
			yield request

	def parse_store(self, response):
		detail = response.xpath('//div[@itemprop="articleBody"]//h1/text()').extract_first()
		store_name = ''
		try:
			store_name = self.getStoreName(detail)
		except:
			pass
		if store_name:
			temp_address = response.xpath('//footer[@id="footer"]//address')[0]
			full_address = self.validate(temp_address.xpath('./span/text()').extract_first())
			phone = self.validate(response.xpath('//div[@class="contact-holder"]/a/text()').extract_first())
			if full_address.find('phone') != -1:
				full_address = self.validate(temp_address.xpath('./text()').extract_first())
			item = ChainItem()
			item['store_name'] = store_name
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(full_address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['phone_number'] = phone
			yield item
		else:
			detail = response.meta['store']
			item = ChainItem()
			item['store_name'] = self.getStoreInfo(detail)[0]
			item['city'] = self.getStoreInfo(detail)[1]
			item['state'] = self.getStoreInfo(detail)[2]
			yield item

	def getStoreInfo(self, item):
		info = ['', '', '']
		item_list = item.split(',')
		info[2] = self.validate(item_list[1])
		item = item_list[0]
		item_list = item.split('-')
		info[0] = self.validate(item_list[0])
		info[1] = self.validate(item_list[1])
		return info
		
	def validate(self, item):
		try:
			item = self.format(item)
			return item.strip()
		except:
			return ''

	def getStoreName(self, item):
		if item.find('Welcome to') != -1:
			item = item.replace('Welcome to', '').replace('!', '')
			return self.validate(item)
		else:
			return ''

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''