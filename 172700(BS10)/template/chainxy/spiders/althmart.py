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

class althmart(scrapy.Spider):
	name = 'althmart'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		for location in self.location_list:
			init_url = 'https://native.healthmart.com/HmNativeSvc/SearchByGpsAllNoState/'+str(location['latitude'])+'/'+str(location['longitude'])+'?apikey=180A0FF6-6659-44EA-8E03-2BE22C2B27A3'
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['StoreName'])
			item['store_number'] = self.validate(str(store['StoreId']))
			item['address'] = self.validate(store['Address'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(store['Zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['Phone'])
			item['latitude'] = self.validate(str(store['Lat']))
			item['longitude'] = self.validate(str(store['Lon']))
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			


	def validate(self, item):
		try:
			return item.strip().replace(';', '').replace('&amp;','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
