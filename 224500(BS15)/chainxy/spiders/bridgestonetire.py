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

class bridgestonetire(scrapy.Spider):
	name = 'bridgestonetire'
	domain = ''
	history = []
	count = 0
	store_number = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.bridgestonetire.com/bin/bridgestone/consumer/bst/api/v1/stores/nearbystores.json?callback=jQuery224004805107136324005_1498327407126&country=US&lat='+str(location['latitude'])+'&lon='+str(location['longitude'])+'&_=1498327407131'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		try:
			data = response.body.split('jQuery224004805107136324005_1498327407126(')[1].strip()[:-2]
			data = data.decode('raw-unicode-escape')
			store_list = json.loads(data)
			if store_list:
				for store in store_list:
					try:
						item = ChainItem()
						item['phone_number'] =  store['phoneNumber']
						item['store_number'] = store['storeNumber']
						item['country'] = 'United States'
						item['latitude'] = store['latitude']
						item['longitude'] = store['longitude']
						item['store_name'] = store['name']
						item['other_fields'] = ""
						item['coming_soon'] = "0"
						item['address'] = store['streetAddress']
						item['address2'] = ''
						item['city'] = store['city']
						item['state'] = self.validate(store['province'])
						item['zip_code'] = self.validate(store['postalCode'])
						item['store_hours'] = "Mon:" + self.parse_time(store['mondayHours']['openTime'])  + " - " +  self.parse_time(store['mondayHours']['closeTime']) + '; '+"Tue:" + self.parse_time(store['tuesdayHours']['openTime'])  + " - " +  self.parse_time(store['tuesdayHours']['closeTime']) + '; '+"Wed:" + self.parse_time(store['wednesdayHours']['openTime'])  + " - " +  self.parse_time(store['wednesdayHours']['closeTime']) + '; '+"Thu:" + self.parse_time(store['thursdayHours']['openTime'])  + " - " +  self.parse_time(store['thursdayHours']['closeTime']) + '; '+"Fri:" + self.parse_time(store['fridayHours']['openTime'])  + " - " +  self.parse_time(store['fridayHours']['closeTime']) + '; '+"Sat:" + self.parse_time(store['saturdayHours']['openTime'])  + " - " +  self.parse_time(store['saturdayHours']['closeTime']) + '; '+"Sun:" + self.parse_time(store['sundayHours']['openTime'])  + " - " +  self.parse_time(store['sundayHours']['closeTime']) + '; '
						if item['store_number'] in self.store_number:
							continue
						self.store_number.append(item['store_number'])
						yield item
					except:
						pdb.set_trace()
		except:
			pdb.set_trace()
	
	def parse_time(self, value):
		try:
			return (datetime.fromtimestamp(int(value)/1000)+timedelta(hours=3)).strftime('%I:%M %p')
		except:
			return ""

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''
