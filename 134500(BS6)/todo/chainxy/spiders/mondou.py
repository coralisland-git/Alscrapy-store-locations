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
import unicodedata

class mondou(scrapy.Spider):
	name = 'mondou'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.mondou.com/api/storelocator/stores'
		payload={
			"page":"1",
			"pageSize":"100",
		}
		header = {
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/json',
			'X-Requested-With':'XMLHttpRequest'
		}
		yield scrapy.Request(url=init_url, headers=header, body=json.dumps(payload), method='POST', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['Stores']
		with open('response.html', 'wb') as f:
			f.write(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['Name'])
				item['store_number'] = self.validate(store['Number'])
				item['address'] = self.validate(store['Address']['Line1'])
				item['address2'] = self.validate(store['Address']['Line2'])
				item['city'] = self.validate(store['Address']['City'])
				item['state'] = self.validate(store['Address']['RegionName'])
				item['zip_code'] = self.validate(store['Address']['PostalCode'])
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store['PhoneNumber'])
				item['latitude'] = self.validate(str(store['Address']['Latitude']))
				item['longitude'] = self.validate(str(store['Address']['Longitude']))
				h_temp = ''
				hour_list = store['Schedule']['OpeningHours']
				for hour in hour_list:
					h_temp += self.validate(hour['LocalizedDay']) + ' ' + self.validate(hour['OpeningTimes'][0]['BeginTime']) + '-' + self.validate(hour['OpeningTimes'][0]['EndTime']) + ', '
				item['store_hours'] = h_temp[:-2]
				yield item				
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''