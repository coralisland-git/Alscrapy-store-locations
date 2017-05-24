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

class wawa(scrapy.Spider):
	name = 'wawa'
	domain = 'https://www.wawa.com/'
	history = ['']
	
	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/geolocation.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url  = 'https://www.wawa.com/Handlers/LocationByLatLong.ashx?limit=200&lat='+str(location['latitude'])+'&long='+str(location['longitude'])
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")		
		data = (response.body.encode("utf8").strip())
		data = json.loads(data)
		for store in data['locations']:
			item = ChainItem()
			item['store_name'] = store['storeName']
			item['store_number'] = store['storeNumber']
			item['address'] = store['addresses'][0]['address']
			item['address2'] = ''
			item['city'] = store['addresses'][0]['city']
			item['state'] = store['addresses'][0]['state']
			item['zip_code'] = store['addresses'][0]['zip']
			item['country'] = 'United States'
			item['phone_number'] = store['telephone']
			item['latitude'] = store['addresses'][1]['loc'][0]
			item['longitude'] = store['addresses'][1]['loc'][1]
			if store['open24Hours'] == True:
				item['store_hours'] = 'open '+ store['openType']
			else :
				item['store_hours'] = store['storeOpen'] + ' - ' + store['storeClose']				
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] not in self.history:
				yield item
				self.history.append(item['store_number'])
			# except:
			# 	pass
