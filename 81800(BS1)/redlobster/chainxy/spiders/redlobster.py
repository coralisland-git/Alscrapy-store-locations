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

class redlobster(scrapy.Spider):
	name = 'redlobster'
	domain = 'https://www.redlobster.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		url_template = "https://www.redlobster.com/api/location/GetLocations?latitude=34.0522342&longitude=-118.2436849&radius=150&limit=26"
		for location in self.location_list:
			url = 'https://www.redlobster.com/api/location/GetLocations?latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&radius=150&limit=26'
			yield scrapy.Request(url=url, callback=self.body)

	def body(self, response):
		data = json.loads(response.body)
		store_list =data['locations']
		
		for store in store_list:
			item = ChainItem()
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(store['location']['address1'])
			item['address2'] = self.validate(store['location']['address2'])
			item['phone_number'] = self.validate(store['location']['phone'])
			item['city'] = self.validate(store['location']['city'])
			item['state'] = self.validate(store['location']['state'])
			item['zip_code'] = self.validate(store['location']['zip'])
			item['country'] = ''
			item['latitude'] = self.validate(store['location']['latitude'])
			item['longitude'] = self.validate(store['location']['longitude'])
			h_temp = ''
			try:
				weekday = ["Sunday", 'Monday', 'Tuesday', 'Wednesday', "Thursday", "Friday", "Saturday"]
				for hour in store['location']['hours']:
					h_temp = h_temp + weekday[hour['dayOfWeek']] + 'open:' + hour['open'] + ' close:' + hour['close'] + ', '
			except:
				pass
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['phone_number'] not in self.history:
				yield item
				self.history.append(item['phone_number'])

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''