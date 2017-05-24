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

class rickysalldaygrillcanada(scrapy.Spider):
	name = 'rickysalldaygrillcanada'
	domain = 'http://gotorickys.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://gotorickys.com/wp-admin/admin-ajax.php'
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest'
		}
		for location in self.location_list:
			formdata = {
				'lat':str(location['latitude']),
				'lng':str(location['longitude']),
				'radius':'100',
				'category':'ALL DAY GRILL',
				'display':'ONLY ACTIVE',
				'action':'csl_ajax_onload'
			}
			yield scrapy.FormRequest(url=init_url, method='POST', formdata=formdata, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['response']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['address'] = self.validate(store['address'])[:-1]
			item['address2'] = self.validate(store['address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			item['store_hours'] = self.validate(store['hours'])
			if self.validate(store['id']) not in self.history:
				self.history.append(self.validate(store['id']))
				yield item			

	def validate(self, item):
		try:
			return item.strip().replace('|', ',').replace('&amp;', ' ').replace(';', '')
		except:
			return ''