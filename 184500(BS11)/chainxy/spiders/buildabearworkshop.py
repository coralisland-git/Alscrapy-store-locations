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

class buildabearworkshop(scrapy.Spider):
	name = 'buildabearworkshop'
	domain = 'http://www.buildabear.com/shopping/storefinder/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.buildabear.com/shopping/storefinder/findAStore.jsp?state='+location['abbreviation']+'#find-by-region'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="stores"]//li//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//section[@id="col1"]//p//text()').extract())
			item['store_name'] = self.validate(detail[0])
			item['coming_soon'] = '0'
			if 'soon' in item['store_name'].lower():
				item['coming_soon'] = '1'
				item['store_name'] = self.validate(item['store_name'].split('-')[0])
			if 'closed' in item['store_name'].lower():
				item['store_name'] = self.validate(item['store_name'].split('- this')[0])
			if 'now' in item['store_name'].lower():
				item['store_name'] = self.validate(item['store_name'].split('-')[0])
			h_temp = ''
			address = ''
			item['phone_number'] = ''
			for de in detail[1:]:
				if ':' in de:
					h_temp += de + ', '
				elif '-' in de and len(de) < 15:
					item['phone_number'] = de
				else:
					address += de + ', '
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
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
		except:
			pass		


	def validate(self, item):
		try:
			return item.strip().replace('\t','').replace('\n','').replace('\r','').replace('  ','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'telephone' not in self.validate(item).lower() and 'fax' not in self.validate(item).lower(): 
				tmp.append(self.validate(item))
		return tmp