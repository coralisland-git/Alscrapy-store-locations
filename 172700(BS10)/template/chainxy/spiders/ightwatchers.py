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

class ightwatchers(scrapy.Spider):
	name = 'ightwatchers'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://api.weightwatchers.com/servicing/v4/meetingfinder/meetinglocations?market=en-us'
		for location in self.location_list:
			payload = {
				"LocationSearchCriteria":{
					"address":{
						"zipCode":location['zipcode']
					},
				"currentPageNumber":"1",
				"ignoreMonthlyPass":"true",
				"numberOfLocationsToReturn":"10",
				"searchDistance":"75",
				"timeOfDay":'All'
				}
			}
			header = {
				"Accept":"application/json, text/plain, */*",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/json;charset=UTF-8"
			}
			yield scrapy.Request(url=init_url, body=json.dumps(payload), headers=header, method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['Location']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(str(store['id']))
			item['address'] = self.validate(store['address']['address1'])
			item['address2'] = self.validate(store['address']['address2'])
			item['city'] = self.validate(store['address']['city'])
			item['state'] = self.validate(store['address']['state'])
			item['zip_code'] = self.validate(store['address']['address']['zipCode'])
			item['country'] = self.validate(store['address']['country'])
			item['latitude'] = self.validate(store['address']['gpsCoordinates']['latitude'])
			item['longitude'] = self.validate(store['address']['gpsCoordinates']['longitude'])
			h_temp = ''
			hour_list = store['meetingsForDay']
			for hour in hour_list:
				h_temp += self.validate(hour['dayOfWeek'])  + ' ' + self.validate(hour['meetings'][0]) + ' ' + self.validate(hour['openHours']) + ', '
			item['store_hours'] = h_temp[:-2]
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
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