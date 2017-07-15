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
import pdb

class sherwinwilliams(scrapy.Spider):
	name = 'sherwinwilliams'
	domain = 'https://www.sherwin-williams.com'
	history = []
	count = 0

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_location_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		kind_list = ['CommercialPaintStore', 'FinishesStore', 'FloorCoveringStore', 'SprayEquipmentStore']
		header = {
					"Accept":"text/plain, */*; q=0.01",
					"Accept-Encoding":"gzip, deflate, br",
					"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
					"X-Requested-With":"XMLHttpRequest"
				}
		init_url = 'https://www.sherwin-williams.com/AjaxStoreLocatorSideBarView?langId=-1&storeId=10151'
		for location in self.US_location_list:
			# for kind in kind_list:
			formdata = {
				"sideBarType":"LSTORES",
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"radius":"75",
				"uom":"SMI",
				"abbrv":"us",
				"address":location['city']+", "+location['state']+", United States",
				# "address":"New York, New York, United States",
				"storeType": 'CommercialPaintStore',
				"requesttype":"ajax",
				"langId":"",
				"storeId":"10151",
				"catalogId":"10001",
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

		# for location in self.CA_location_list:
		# 	for kind in kind_list:
		# 		formdata = {
		# 			"sideBarType":"LSTORES",
		# 			"latitude":str(location['latitude']),
		# 			"longitude":str(location['longitude']),
		# 			"radius":"200",
		# 			"uom":"SMI",
		# 			"abbrv":"ca",
		# 			"address":location['city'].split('(')[0].strip()+", "+location['state']+", Canada",
		# 			# "address":"Los Angeles, California, United States",
		# 			"storeType": kind,
		# 			"requesttype":"ajax",
		# 			"langId":"",
		# 			"storeId":"10151",
		# 			"catalogId":"10001",
		# 		}
		# 		yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)
		

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('.//ul[@id="storeResults"]//h5[@class="font-weight--bold"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('.//div[@class="sw-col--1-1 sw-col-md--1-2"][1]//text()').extract())
			item['address'] = detail[0]			
			item['city'] = detail[1]
			item['state'] = detail[2].upper()
			item['zip_code'] = detail[3]
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = detail[4]
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('.//div[@class="sw-col--1-1 sw-col-md--1-2 store-hours-table"]//text()').extract())
			cnt = 1
			for hour in hour_list[1:-1]:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\t','').replace('\xa0','').replace(',','')
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

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''
