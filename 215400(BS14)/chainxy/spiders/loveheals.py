# from __future__ import unicode_literals
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

class loveheals(scrapy.Spider):
	name = 'loveheals'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/3748/stores.js?callback=storeMapperCallback2'
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body.split('storeMapperCallback2(')[1][:-1].strip())['stores']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(str(store['id']))
				address = self.validate(store['address'])
				if 'canada' in address.lower():
					try:
						address = address.replace('canada', '').replace('Canada','').replace('CANADA','')
						address = address.split(',')
						a_temp = ''
						for addr in self.eliminate_space(address[0].split(' '))[:-1]:
							a_temp += addr + ' ' 
						item['address'] = self.validate(a_temp)
						item['city'] = self.eliminate_space(address[0].split(' '))[-1]
						item['state'] = self.eliminate_space(address[1].split(' '))[0]
						z_temp = ''
						for addr in self.eliminate_space(address[1].split(' '))[1:]:
							z_temp += addr + ' '
						item['zip_code'] = self.validate(z_temp)
						item['country'] = 'CA'
					except:
						address = address.split(' ')
						a_temp = ''
						for addr in address[:-3]:
							a_temp += addr + ' ' 
						item['address'] = self.validate(a_temp)
						item['city'] = address[-3]
						item['state'] = address[-2]
						item['zip_code'] = address[-1]
						item['country'] = 'CA'	
				else:
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
				address = address.upper()[:-8].strip()
				a_list = item['store_name'].upper().split(' ')
				for a in a_list:
					address = self.validate(address.replace(a, '')).replace(',','')
				item['address'] = address
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
				if item['country'] == 'US' or item['country'] == 'CA':
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