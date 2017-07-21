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

class schubachjewelers(scrapy.Spider):
	name = 'schubachjewelers'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.schubachjewelers.com/ustorelocator/location/searchJson/'
		header = {
			"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
			"Accept-Encoding":"gzip, deflate",
			"Content-type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"radius":"25",
				"address":location['city'],
				"lat":str(location['latitude']),
				"lng":str(location['longitude']),
				"loc_type":"locality",
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['markers']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['title'])
					item['store_number'] = self.validate(store['store_id'])
					item['address'] = self.validate(store['address']).split(',')[0]
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zipcode'])
					item['country'] = self.validate(store['country'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					item['store_hours'] = self.validate(store['storehours'])
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						if 'Schubach Jewelers' in item['store_name']:
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