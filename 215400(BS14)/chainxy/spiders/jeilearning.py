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

class jeilearning(scrapy.Spider):
	name = 'jeilearning'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://us.jei.com/JEI-Centers/Find-Center'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = self.validate(response.body.split('var locations = [')[1].split('var map = ')[0].strip()[1:-2])[:-1].split('], [')
		for store in store_list:
			try:
				detail = self.eliminate_space(etree.HTML(store).xpath('//text()'))
				item = ChainItem()
				item['store_name'] = detail[0].split('(')[0].strip()
				item['phone_number'] = ''
				address = ''
				for cnt in range(1, len(detail)):
					if 'email' in detail[cnt+1].lower():
						item['phone_number'] = detail[cnt]
						break
					address += detail[cnt]
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
				if item['country'] != 'US':
					item['state'] = address.split(',')[-1].strip()[:2].strip()
					item['zip_code'] = address.split(',')[-1].strip()[2:].strip()
					item['country'] = "CA"
				geo_list = self.eliminate_space(detail[-1].split(','))
				item['latitude'] = geo_list[0]
				item['longitude'] = geo_list[1]
				yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\t','').replace('\r','').replace('\\n','').replace('\\t','').replace('\\r','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != "'" :
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
			if item in state['abbreviation']:
				return state['country']
		return ''
