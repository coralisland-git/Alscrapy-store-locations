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

class mycountymarket(scrapy.Spider):
	name = 'mycountymarket'
	domain = 'http://www.mycountymarket.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.mycountymarket.com/shop/store-locator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store-locator-search-results"]//td[1]//a/@href').extract()
		for store in store_list:
			try:
				store = self.domain + store
				yield scrapy.Request(url=store, callback=self.parse_page)
			except:
				pass
	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="content"]//div[2]//div[1]//div//div//text()').extract())
			ind = 0
			address = ''
			for cnt in range(0,len(detail)-1):
				if 'Map' in detail[cnt]:
					ind = cnt
					break
			for cnt in range(1, ind):
				address += detail[cnt] + ', '
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
			item['country'] = 'United States'
			for cnt in range(0,len(detail)-1):
				if 'Phone' in detail[cnt]:
					item['phone_number'] = self.validate(detail[cnt+1])	
					break
			for cnt in range(0,len(detail)-1):
				if 'Hours' in detail[cnt]:
					item['store_hours'] = self.validate(detail[cnt+1])	
					break	
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''