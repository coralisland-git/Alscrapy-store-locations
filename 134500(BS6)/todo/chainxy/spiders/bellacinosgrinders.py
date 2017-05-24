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

class Bellacinosgrinders(scrapy.Spider):
	name = 'bellacinosgrinders'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.blipstar.com/blipstarplus/viewer/searchdbnew?uid=6302145&lat=%s&lng=%s&type=radius&value=500&keyword=&max=500' %(str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				addr = self.validate(store['ad']).split(',')
				item['store_name'] = self.validate(store['n'])
				if len(addr) == 4:
					item['address'] = self.validate(addr[0])
					item['city'] = self.validate(addr[1])
					item['state'] = self.validate(addr[2])
					item['zip_code'] = self.validate(addr[3])
				else:
					item['address'] = self.validate(addr[0])
					item['address2'] = self.validate(addr[1])
					item['city'] = self.validate(addr[2])
					item['state'] = self.validate(addr[3])
					item['zip_code'] = self.validate(addr[4])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['p'])
				item['latitude'] = self.validate(str(store['lat']))
				item['longitude'] = self.validate(str(store['lng']))
				if item['phone_number'] not in self.history:
					self.history.append(item['phone_number'])
					yield item			
			except:
				pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''