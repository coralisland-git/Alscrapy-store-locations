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

class vetcoclinics(scrapy.Spider):
	name = 'vetcoclinics'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.vetcoclinics.com/_assets/dynamic/ajax/locator.php?zip='+str(location['zipcode'])
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['clinics']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['title'])
					data = self.validate(store['label'])
					tree = etree.HTML(data)
					detail = self.eliminate_space(tree.xpath('//address//text()'))
					item['phone_number'] = ''
					address = ''
					for de in detail:
						if '-' in de and len(de) < 15:
							item['phone_number'] = de
						else:
							address += de + ' '
					item['address'] = ''
					item['city'] = ''
					addr = usaddress.parse(self.validate(address))
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
					item['latitude'] = self.validate(store['point']['lat'])
					item['longitude'] = self.validate(store['point']['long'])
					h_temp = ''
					hour_list = self.eliminate_space(tree.xpath('//div[@class="timeinfo_area"]//text()'))
					cnt = 1
					for hour in hour_list:
						if cnt % 2 == 0:
							h_temp += self.validate(hour.replace('at','')) + ', '
						else:
							h_temp += self.validate(hour) +' '
						cnt += 1
					item['store_hours'] = h_temp[:-2]
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
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
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''