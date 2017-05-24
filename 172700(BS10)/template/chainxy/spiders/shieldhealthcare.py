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

class shieldhealthcare(scrapy.Spider):
	name = 'shieldhealthcare'
	domain = 'http://www.shieldhealthcare.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.shieldhealthcare.com/community/'
		yield scrapy.Request(url=init_url, callback=self.body) 
		# yield scrapy.Request(url="http://www.shieldhealthcare.com/community/texas/", callback=self.parse_page)

	def body(self, response):
		print("=========  Checking.......")
		# with open('response.html', 'wb') as f:
		# 	f.write(response.body)
		state_list = response.xpath('//div[contains(@class, "homeCategoryGry")]//a/@href').extract()
		for state in state_list:
			if state != '#':
				state = self.domain + state
				yield scrapy.Request(url=state, callback=self.parse_page)

	def parse_page(self, response):
		print("=========  Checking.......")	
		store_list = response.xpath('//div[@id="tabs-3"]/div')
		try:
			item = ChainItem()
			store = response.xpath('//div[@id="tabs-3"]')
			address_temp = self.eliminate_space(store.xpath('./text()').extract())
			address = ''
			for temp in address_temp:
				if '(' not in temp:
					address += temp + ', '		
				else:
					item['phone_number'] = temp
					break
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			if item['phone_number'] != '':
				yield item
		except:
			pass

		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//strong/text()').extract_first())
				address_temp = self.eliminate_space(store.xpath('./text()').extract())
				address = ''
				for temp in address_temp:
					address += temp + ', '		
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//div[@class="phoneNumberBox"]/text()').extract_first())
				if item['store_name'] != '':
					yield item			
			except:
				pdb.set_trace()
			

		
	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('\r','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp