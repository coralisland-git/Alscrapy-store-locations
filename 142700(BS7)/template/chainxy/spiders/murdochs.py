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
import pdb

class murdochs(scrapy.Spider):
	name = 'murdochs'
	domain = 'http://www.murdochs.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.murdochs.com/stores/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="side-store-links"]//div[@class="store-link"]//a/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		detail = self.eliminate_space(response.xpath('//div[@class="store-info left-side"][1]//span[@class="store-info-content"]//text()').extract())
		address = ''
		for de in detail:
			if 'phone' not in de.lower():
				address += de +', '
			else:
				item['phone_number'] = de.split(':')[1].strip()
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(address)
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += temp[0].replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] = temp[0]
			elif temp[1] == 'ZipCode':
				item['zip_code'] = temp[0].replace(',','')
			else:
				item['address'] += temp[0].replace(',', '') + ' '
		h_temp = ''
		hour_list = self.eliminate_space(response.xpath('//div[@class="store-info right-side"][1]//span[@class="store-info-content"]//text()').extract())
		for hour in hour_list:
			if '-' in hour:
				h_temp += hour + ', '
		item['store_hours'] = h_temp[:-2]
		yield item			


	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''
