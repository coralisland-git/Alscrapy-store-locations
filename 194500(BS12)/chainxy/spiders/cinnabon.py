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

class cinnabon(scrapy.Spider):
	name = 'cinnabon'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		for location in self.location_list:
			init_url = 'https://www.cinnabon.com/Location/Map/Get?brand=%7Ba019d0e8-a707-40cc-b647-f3a4670ae0ab%7D&bounds='+str(location['latitude']-0.2943)+'%2C'+str(location['longitude']-0.8767)+'%2C'+str(location['latitude']+0.2943)+'%2C'+str(location['longitude']+0.8769)+'&addressLatitude='+str(location['latitude'])+'&addressLongitude='+str(location['longitude'])+'&useCache=false&userfilters=8c753773-7ff5-4f6f-a550-822523cbafad&userfilters=3431a520-d000-46bb-9058-b000edc96867&userfilters=43ba8d22-b606-4d69-8b91-437e5d6264fd'
			yield scrapy.Request(url=init_url,headers=header, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)['Locations']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['LocationName'])
			item['address'] = self.validate(store['StreetAddress'])
			item['city'] = self.validate(store['Locality'])
			item['state'] = self.validate(store['Region'])
			item['zip_code'] =self.validate(store['PostalCode'])
			item['country'] = self.validate(store['CountryName'])
			item['phone_number'] = self.validate(store['Tel'])
			item['latitude'] = self.validate(str(store['Latitude']))
			item['longitude'] = self.validate(str(store['Longitude']))
			h_temp = ''
			week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			for week in week_list:
				try:
					h_temp += week + ' ' + store['Hours'][week] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			if item['country'] == 'United States of America':
				if item['address'] + item['phone_number'] not in self.history:
					self.history.append(item['address'] + item['phone_number'])
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
