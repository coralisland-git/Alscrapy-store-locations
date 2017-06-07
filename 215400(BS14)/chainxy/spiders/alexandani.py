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

class alexandani(scrapy.Spider):
	name = 'alexandani'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.alexandani.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table[@class="aa-locations"]/tr/td')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['phone_number'] = ''
				item['store_name'] = detail[0]
				address = ''
				addr = address.split(',')
				item['address'] = detail[1]
				try:
					item['city'] = detail[2].split(',')[0].strip()
					item['state'] = detail[2].split(',')[1].strip()[:2]
					item['zip_code'] = detail[2].split(',')[1].strip()[2:]
				except:
					item['city'] = detail[3].split(',')[0].strip()
					item['state'] = detail[3].split(',')[1].strip()[:2]
					item['zip_code'] = detail[3].split(',')[1].strip()[2:]
				item['country'] = 'United States'
				h_temp = ''
				count = 0
				for ind in range(0, len(detail)):
					if '(' in detail[ind] and '-' in detail[ind]: 
						item['phone_number'] = detail[ind]
					if 'hours' in detail[ind].lower():
						count = ind+1
						break
				cnt = 1
				for ind in range(count, len(detail)):
					h_temp += detail[ind]
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['zip_code'] == '2571':
					pdb.set_trace()
				yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\r','').replace('\n','').replace('  ','')
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