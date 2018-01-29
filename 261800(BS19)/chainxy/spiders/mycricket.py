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
import tokenize
import token
from StringIO import StringIO

class mycricket(scrapy.Spider):
	name = 'mycricket'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://momentfeed-prod.apigee.net/api/llp/cricket.json?auth_token=IVNLPNUOBXFPALWE&center='+str(location['latitude'])+','+str(location['longitude'])+'&coordinates='+str(location['latitude']-47.042)+','+str(location['longitude']+53.2832)+','+str(location['latitude']+27.7846)+','+str(location['longitude']-53.2832)+'&name=Cricket+Wireless+Authorized+Retailer,Cricket+Wireless+Store&page=1&pageSize=500&type=store'
			header = {
				"Accept":"application/json, text/plain, */*",
				"Accept-Encoding":"gzip, deflate, br"
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for store in store_list:
			store = store['store_info']
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['address'] = self.validate(store['address'])				
			item['city'] = self.validate(store['locality'])
			item['state'] = self.validate(store['region'])
			item['zip_code'] = self.validate(store['postcode'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	

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
