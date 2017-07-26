from __future__ import unicode_literals
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

class seattlesbest(scrapy.Spider):
	name = 'seattlesbest'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			zipcode = str(location['zipcode'])
			for ind in range(0, 5-len(zipcode)):
				zipcode = '0'+zipcode
			init_url = 'https://seattlesbest.com/sbuxpld//stores.php?zip='+zipcode+'&radius=1000&upcs=1291901254,1291900888,1291912261,1291912645,1291900943,1291901132,1291912231,1291912130,1291901244,1291901245,1291901272,1291901113,1291901156,1291901216,1291998621,1291901274,1291901206,1291901224,1291901225,1291901275,1291901217,1291901273,1291901220,6211188553,1291912310,1291901215,1291901223,1291912050,1291901218,1291901219,1291912340,1291912211'
			header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, br",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		try:
			store_list = json.loads(response.body)['Stores']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['Name'])
					item['store_number'] = self.validate(store['Id'])
					item['address'] = self.validate(store['Address'])
					item['city'] = self.validate(store['City'])
					item['state'] = self.validate(store['State'])
					item['zip_code'] = self.validate(store['ZIPCode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['Phone'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					if item['store_number'] not in self.history:
						self.history.append(item['store_number'])
						yield item	
				except:
					pdb.set_trace()		
		except:
			pass

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