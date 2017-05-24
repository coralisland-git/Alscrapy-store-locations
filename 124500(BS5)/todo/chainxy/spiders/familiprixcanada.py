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
import unicodedata

class familiprixcanada(scrapy.Spider):
	name = 'familiprixcanada'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.familiprix.com/webservices/branchsearch.asmx/AdvSearchByCurrentPo'
		header={
				'Accept':'*/*',
				'Accept-Encoding':'gzip, deflate',
				'Content-Type':'application/json; charset=UTF-8',
				'X-Requested-With':'XMLHttpRequest'
			}
		for location in self.location_list:
			data = {"accessModes":[],"genServices":[],"isPharmacyZone":"false","lat":str(location['latitude']),"lg":location['longitude'],"profServices":[]}
			yield scrapy.Request(url=init_url, method="POST", body=json.dumps(data), headers=header, callback=self.body) 

	def body(self, response):
		print('~~~~~~~~~~ checking .............')
		try:
			store_list = json.loads(response.body)['d']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['Name'])
				item['address'] = self.validate(store['Address'])
				item['city'] = self.validate(store['City'])
				item['state'] = self.validate(store['Province'])
				item['zip_code'] = self.validate(store['PostalCode'])
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store['PhoneNumber'])
				item['latitude'] = str(store['Latitude'])
				item['longitude'] = str(store['Longitude'])
				h_temp = ''
				hour_list = store['WeekSchedule']
				for hour in hour_list:
					h_temp += self.validate(hour['Key']) + ' ' + self.validate(hour['Value']) +', '
				item['store_hours'] = h_temp[:-2]
				if item['store_name']+item['phone_number'] not in self.history:
					self.history.append(item['store_name']+item['phone_number'])
					yield item			
		except:
			pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(' a ', '-')
		except:
			return ''