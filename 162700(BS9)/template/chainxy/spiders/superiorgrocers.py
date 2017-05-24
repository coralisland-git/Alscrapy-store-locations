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

class superiorgrocers(scrapy.Spider):
	name = 'superiorgrocers'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://superiorgrocers.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@id, "locations")]//div[@class="location"]')
		for store in store_list:
			detail = self.eliminate_space(store.xpath('.//p/text()').extract())
			item = ChainItem()
			name = store.xpath('.//h3/text()').extract_first()
			item['store_name'] = self.validate(name.split('#')[0])
			item['store_number'] = self.validate(name.split('#')[1])
			address = ''
			for de in detail:
				if '-' in de:
					if '(' in de:
						item['phone_number'] = de
					else :
						item['store_hours'] = de
				else:
					address += de + ' '
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''