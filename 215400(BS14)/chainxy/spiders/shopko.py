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
import pdb

class shopko(scrapy.Spider):
	name = 'shopko'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.shopko.com/custserv/locate_store.cmd'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		for location in self.location_list:
			formdata = {
				"useCurrentLocation":"yes",
				"latitude":"",
				"longitude":"",
				"cityStateZip":location['city'],
				"search-submit":"",
				"radius":"500",
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)
		
	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('var stores = [')[1].split('</script>')[0][2:-3]
			store_list = data.split('],[')
			for store in store_list:
				try:
					detail = self.eliminate_space(store.split("','"))
					item = ChainItem()
					item['store_name'] = detail[2].split(':')[1].strip()
					item['address'] = detail[3]			
					address = detail[6]
					addr = address.split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['country'] = 'United States'
					item['phone_number'] = detail[7]
					item['store_hours'] = self.validate(detail[8])[:-1]
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('<br>', ',')
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