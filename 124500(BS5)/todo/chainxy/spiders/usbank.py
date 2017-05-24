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
import pdb

class usbank(scrapy.Spider):
	name = 'usbank'
	domain = 'https://www.usbank.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://publicrestservice.usbank.com/public/ATMBranchLocatorRESTService_V_8_0/GetListATMorBranch/LocationSearch/StringQuery?&callback=myCallback&output=json&application=USBMOBIL&transactionid=83962be7-688e-424f-a762-c8c365eca722&stringquery=%s&searchtype=E&' %location['city']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('myCallback(')[1].strip()[:-1]
			store_list = json.loads(data)['GetListATMorBranchReply']['BranchList']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = store['Name']
				item['store_number'] = store['Identifier']
				address = store['LocationIdentifier']['Address']
				item['address'] = address['AddressLine1']
				item['address2'] = address['AddressLine2']
				item['city'] = address['City']
				item['state'] = address['StateCode']
				item['zip_code'] = address['ZipCode']
				item['country'] = address['CountryCode']
				item['phone_number'] = store['PhoneNumber']
				geolocation = store['LocationIdentifier']['GeocodeLocation']
				item['latitude'] = geolocation['Latitude']
				item['longitude'] = geolocation['Longitude']
				h_temp = ''
				week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
				hour_list = store['OperationalHours']
				for week in week_list:
					h_temp += week + ' ' + hour_list[week]['OpeningTime'] + '-' + hour_list[week]['ClosingTime'] + ', '
				item['store_hours'] = h_temp[:-2]
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['store_name']+item['store_number'] not in self.history:
					self.history.append(item['store_name']+item['store_number'])
					yield item	
		except:
			pass		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''