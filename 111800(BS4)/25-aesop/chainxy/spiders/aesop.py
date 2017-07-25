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

class aesop(scrapy.Spider):
	name = 'aesop'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		with open(script_dir + '/geo/US_States.json') as data_file:
			self.state_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.aesop.com/usa/ustorelocator/location/search/?regionId=3&state='+location['state']+'&city='+location['city']+'&postcode=false&latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&geocodedState=false&geocodedCountry=false'
			yield scrapy.Request(url=init_url, callback=self.body) 
	def body(self, response):
		# print("=========  Checking.......")
		try:
			store_list = response.xpath('//marker')
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('./@title'))
				item['store_number'] = self.validate(store.xpath('./@location_id'))
				address = self.validate(store.xpath('./@address_display'))
				if len(address) >30 :
					address = self.validate(store.xpath('./@address'))
				addr = usaddress.parse(address)
				item['address'] = ''
				item['city'] = ''
				item['country'] = ''
				item['state'] = self.validate(store.xpath('./@state'))
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
				item['phone_number'] = self.validate(store.xpath('./@phone'))
				item['latitude'] = self.validate(store.xpath('./@latitude'))
				item['longitude'] = self.validate(store.xpath('./@longitude'))
				item['store_hours'] = self.validate(store.xpath('./@tradinghours'))
				item['store_type'] = self.validate(store.xpath('./@store_type'))
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					if self.check(item['state'].strip()):
						item['country'] = 'United States'
						yield item	
		except:
			pdb.set_trace()		

	def check(self, item):
		cnt = 0
		for state in self.state_list:
			if item == state['abbreviation']:
				cnt += 1

		if cnt != 0:
			return True
		else :
			return False

	def validate(self, item):
		try:
			item = item.extract_first().strip()
			mark_list = ['\t', '\r', '\n', ',', ';', '>b', '<br>', '</br>', '<BR>', '<ul>', '</ul>', '<u>', '</u>']
			for mark in mark_list:
				item  = item.replace(mark, ' ')
			item = unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
			return item
		except:
			return ''

