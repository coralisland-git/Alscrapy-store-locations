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

class firstam(scrapy.Spider):
	name = 'firstam'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			# init_url = 'http://www.firstam.com/webservices/FirstAMDirectoryServices/DirectoryService.svc/ProximitySearch?t=1495196279499&&coords='+str(location['latitude'])+','+str(location['longitude'])+'&proximity=25&officeTypes=1002%2C%201006%2C%201007%2C%201008%2C%201009%2C%201010%2C%201011%2C%201012%2C%201027%2C%201029%2C%201030%2C%201035%2C%201038'
			init_url = 'http://www.firstam.com/webservices/FirstAMDirectoryServices/DirectoryService.svc/OfficesAndCitiesInCounty?t=1495196279499&&state='+location['state']+'&county='+location['city']+'&officeTypes=1002%2C%201006%2C%201007%2C%201008%2C%201009%2C%201010%2C%201011%2C%201012%2C%201027%2C%201029%2C%201030%2C%201035%2C%201038'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['ProximitySearchResult']['Offices']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['CompanyName'])
				item['store_number'] = self.validate(str(store['OfficeID']))
				item['address'] = self.validate(store['Address1'])
				item['address2'] = self.validate(store['Address2'])
				item['city'] = self.validate(store['City'])
				item['state'] = self.validate(store['State'])
				item['zip_code'] = self.validate(store['Zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['Phones'][0]['PhoneNumber'])
				item['latitude'] = self.validate(str(store['Latitude']))
				item['longitude'] = self.validate(str(store['Longitude']))
				item['store_type'] = self.validate(store['OfficeType'])
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
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