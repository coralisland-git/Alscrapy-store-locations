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

class jiffylube(scrapy.Spider):
	name = 'jiffylube'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.jiffylube.ca/Locations/GeocodeAddress'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"fieldValue":location['city'].split('(')[0].strip()
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['Stores']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = 'Service Centre'
					item['store_number'] = self.validate(str(store['Store_Number']))
					item['address'] = self.validate(store['Address_Line_1'])
					item['address2'] = self.validate(store['Address_Line_2'])
					item['city'] = self.validate(store['City'])
					item['state'] = self.validate(store['Region_State'])
					item['zip_code'] = self.validate(store['Postal_Code'])
					item['country'] = self.validate(store['Country'])
					item['phone_number'] = self.validate(store['Phone_Number'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					h_temp = ''
					hour_list = store['FormattedHours']
					cnt = 1
					for hour in hour_list:
						h_temp += hour + ', '
					item['store_hours'] = h_temp[:-2]
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