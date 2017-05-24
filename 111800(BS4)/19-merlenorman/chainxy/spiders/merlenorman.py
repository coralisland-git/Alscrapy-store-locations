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

class merlenorman(scrapy.Spider):
	name = 'merlenorman'
	domain = 'http://www.merlenorman.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			payload = '{"request":{"appkey":"3FC04602-C261-11DD-B20A-854637ABAA09","formdata":{"geoip":false,"dataview":"store_default","limit":500,"geolocs":{"geoloc":[{"addressline":"","country":"","latitude":'+str(location['latitude'])+',"longitude":'+str(location['longitude'])+'}]},"searchradius":"500","where":{"or":{"retail":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"promo":{"eq":""}}},"false":"0"}}}'
			init_url = 'http://hosted.where2getit.com/merlenorman/rest/locatorsearch?lang=en_US'
			yield scrapy.Request(url=init_url, method="post", body=payload, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['response']['collection']
		for store in store_list:
			item = ChainItem()
			if 'name' in store:
				item['store_name'] = self.validate(store['name'])
			item['store_number'] = ''
			item['address'] = store['address1']
			if str(store['address2']) != 'None':
				item['address2'] = store['address2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['postalcode']
			item['country'] = store['country']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			item['phone_number'] = ''
			if 'phone' in store:
				item['phone_number'] = store['phone']
			h_temp = ''
			try:
				week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
				for week in week_list:
					if str(store[week]) != 'None':
						h_temp += week + ' ' + store[week] + ', '
				item['store_hours'] = h_temp[:-2]
			except:
				pass
			if item['address']+item['phone_number'] not in self.history:
				if item['country'] == 'US':
					self.history.append(item['address']+item['phone_number'])
					yield item		
		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''