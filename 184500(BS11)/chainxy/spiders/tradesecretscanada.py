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

class tradesecretscanada(scrapy.Spider):
	name = 'tradesecretscanada'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://talk.tradesecrets.ca/locations-reviews/'	
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@rel="noopener noreferrer"]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "fusion-one-half fusion-layout-column fusion-spacing-no")]//h4//text()').extract())
			h_temp = ''
			for de in detail:
				if '(' in de and '-' in de:
					try:
						item['phone_number'] = self.validate('(' + de.split('(')[1])
					except:
						item['phone_number'] = self.validate(de)
				if ':' in de:
					h_temp += de + ', '
			if '(' in detail[0]:
				detail[0] = self.validate(detail[0].split('(')[0]).replace('|','')
			addr = detail[0].replace('|','').split(',')
			if len(addr) == 4:
				item['address'] = self.validate(addr[1])
				item['city'] = self.validate(addr[2])
				item['state'] = self.validate(addr[3].strip())[:2].strip()
				item['zip_code'] = self.validate(addr[3])[2:].strip()
			elif len(addr) == 3:
				item['address'] = self.validate(addr[0])
				item['city'] = self.validate(addr[1])
				item['state'] = self.validate(addr[2].strip())[:2].strip()
				item['zip_code'] = self.validate(addr[2])[2:].strip()
			else:
				pdb.set_trace()
			item['country'] = 'Canada'
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass


	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '').replace('\xa0', '').replace('|','').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'try' not in self.validate(item).lower() and 'http' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp