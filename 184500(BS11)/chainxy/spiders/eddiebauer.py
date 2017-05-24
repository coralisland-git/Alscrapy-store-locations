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

class eddiebauer(scrapy.Spider):
	name = 'eddiebauer'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_US = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_CA = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list_US:
			init_url = 'http://spatial.virtualearth.net/REST/v1/data/53b7a46be2ea4c5dad6ae080825a7784/eddiebauer/eddiebauerstores?spatialFilter=nearby('+str(location['latitude'])+','+str(location['longitude'])+',160.9344)&$select=EntityID,Name,AddressLine,Latitude,Longitude,PrimaryCity,SubDivision,PostalCode,Phone,StoreHours,StoreType,__Distance&$orderby=PostalCode&key=AmowNsVsJ4HTBQJvG2tx3T3IJkeLBfMjwxFfLWx8Ngum6VkACf8XZKOghfBw_eoi&$format=json&jsonp=jQuery17205829111608686792_1495264964242&_=1495265072693'
			header = {
				"Accept":"*/*",
				"Accept-Encoding":"gzip, deflate, sdch"
			}		
			yield scrapy.Request(url=init_url, headers=header, callback=self.body, meta={'country':'United States'}) 

		for location in self.location_list_CA:
			init_url = 'http://spatial.virtualearth.net/REST/v1/data/53b7a46be2ea4c5dad6ae080825a7784/eddiebauer/eddiebauerstores?spatialFilter=nearby('+str(location['latitude'])+','+str(location['longitude'])+',160.9344)&$select=EntityID,Name,AddressLine,Latitude,Longitude,PrimaryCity,SubDivision,PostalCode,Phone,StoreHours,StoreType,__Distance&$orderby=PostalCode&key=AmowNsVsJ4HTBQJvG2tx3T3IJkeLBfMjwxFfLWx8Ngum6VkACf8XZKOghfBw_eoi&$format=json&jsonp=jQuery17205829111608686792_1495264964242&_=1495265072693'
			header = {
				"Accept":"*/*",
				"Accept-Encoding":"gzip, deflate, sdch"
			}		
			yield scrapy.Request(url=init_url, headers=header, callback=self.body, meta={'country':'Canada'}) 

	def body(self, response):
		store_list = json.loads(response.body.split('jQuery17205829111608686792_1495264964242(')[1].strip()[:-1])['d']['results']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['Name'])
				item['store_number'] = self.validate(store['EntityId'])
				item['address'] = self.validate(store['AddressLine'])
				item['city'] = self.validate(store['PrimaryCity'])
				item['state'] = self.validate(store['SubDivision'])
				item['zip_code'] = self.validate(store['PostalCode'])
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(store['Phone'])
				item['latitude'] = self.validate(str(store['Latitude']))
				item['longitude'] = self.validate(str(store['Longitude']))
				item['store_hours'] = self.validate(store['StoreHours'])
				item['store_type'] = self.validate(store['StoreType'])
				if item['store_number']+item['phone_number'] not in self.history:
					self.history.append(item['store_number']+item['phone_number'])
					yield item	
			except:
				pdb.set_trace()		

	def check_country(self, item):
		for state in self.US_States_list:
			if item in state['abbreviation']:
				return 'United States'
		return 'Canada'

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