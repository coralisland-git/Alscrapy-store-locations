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
import tokenize
import token
from StringIO import StringIO

class serta(scrapy.Spider):
	name = 'serta'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.US_Zip_list = json.load(data_file)

	def start_requests(self):
		for location in self.US_Zip_list:
			try:
				init_url = 'https://www.serta.com/store-locator'
				header = {
					"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					"Accept-Encoding":"gzip, deflate, br",
					"Content-Type":"application/x-www-form-urlencoded"
				}
				zipcode = str(location['zipcode'])
				for ind in range(0, 5-len(zipcode)):
					zipcode = '0'+zipcode
				formdata = {
					"zip":zipcode,
					"filter":""
				}
				yield scrapy.FormRequest(url=init_url, method="post", headers=header, formdata=formdata, callback=self.body) 
			except:
				pass

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('PageData.dealerMap = ')[1].strip().split('var PageData')[0].strip()
			store_list = json.loads(data)['locations']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['name'])
					item['store_number'] = self.validate(str(store['id']))
					item['address'] = self.validate(store['address'])
					item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zip'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(str(store['lat']))
					item['longitude'] = self.validate(str(store['long']))
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pdb.set_trace()	
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

	def get_zipcode(self, item):
		for zipcode in self.US_Zip_list:
			if item.lower() in zipcode['city'].lower():
				return zipcode
				break
		return ''