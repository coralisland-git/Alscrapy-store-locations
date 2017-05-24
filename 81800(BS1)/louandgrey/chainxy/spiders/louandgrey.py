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

class louandgrey(scrapy.Spider):
	name = 'louandgrey'
	domain = 'https://www.louandgrey.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/geocode.json'
		with open(file_path) as data_file:    
		    self.location_list = json.load(data_file)

	def start_requests(self):
		
	    for location in self.location_list:
			init_url = 'https://annstorelocator.appspot.com/stores?limit=150&lng='+str(location['longitude'])+'&lat='+str(location['latitude'])+'&Company=ATL%2CLOS%2CLGS'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = json.loads(response.body)
		store_list = data['features']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['properties']['Store_Name']
			item['store_number'] = store['properties']['Store_Id']
			item['address'] = store['properties']['Store_Address1']
			item['address2'] = ''
			item['city'] = store['properties']['Store_City']
			item['state'] = store['properties']['Store_State']
			item['zip_code'] = store['properties']['Store_Zip']
			item['country'] = store['properties']['Country_Id']
			item['phone_number'] = store['properties']['Store_Phone']
			item['latitude'] = store['geometry']['coordinates'][0]
			item['longitude'] = store['geometry']['coordinates'][1]
			item['store_hours'] = store['properties']['Mon_Open'] + '-' + store['properties']['Mon_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Tue_Open'] + '-' + store['properties']['Tue_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Wed_Open'] + '-' + store['properties']['Wed_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Thu_Open'] + '-' + store['properties']['Thu_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Fri_Open'] + '-' + store['properties']['Fri_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Sat_Open'] + '-' + store['properties']['Sat_Close']
			item['store_hours'] = item['store_hours'] + ', ' +store['properties']['Sun_Open'] + '-' + store['properties']['Sun_Close']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_name']+str(item['store_number']) not in self.history:
				yield item
				self.history.append(item['store_name']+str(item['store_number']))
