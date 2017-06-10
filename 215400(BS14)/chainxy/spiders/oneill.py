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

class oneill(scrapy.Spider):
	name = 'oneill'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://us.oneill.com/dealers/?gmw_post=dealer&gmw_address%5B0%5D='+str(location['zipcode'])+'&gmw_distance=200&gmw_units=imperial&gmw_form=1&gmw_per_page=5&gmw_lat&gmw_lng&gmw_px=pt&action=gmw_post'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="dealer-location vcard"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h2[@class="dealer-location__name org"]/text()').extract_first())
				detail = self.eliminate_space(store.xpath('.//div[@class="dealer-location__address adr"]//text()').extract())
				address = detail[0]
				if 'USA' in detail[0]:
					address = detail[0].replace('USA','').strip()[:-1]
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

				item['country'] = self.check_country(item['state'])
				if item['country'] == '' or item['country'] == 'CA':
					item['state'] = address.split(',')[1].strip()[:2]
					item['zip_code'] = address.split(',')[1].strip()[2:].strip()
					item['country'] = 'CA'
				item['phone_number'] = ''
				for de in detail:
					if '(' in de:
						item['phone_number'] = de
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass

		pagenation = response.xpath('//div[@class="dealer__list__pagination"]//a[2]/@href').extract_first()
		if pagenation:
			yield scrapy.Request(url=pagenation, callback=self.body)

	def validate(self, item):
		try:
			return item.strip().replace('\u2019', "'")
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''