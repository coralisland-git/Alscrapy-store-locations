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

class stewartsshops(scrapy.Spider):
	name = 'stewartsshops'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.stewartsshops.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=500&radius=500&autoload=1' %(location['latitude'], location['longitude'])
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['store']).replace('&#038;','').replace('&#8211;','')
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				h_temp = ''
				hour_list = etree.HTML(store['hours']).xpath('//table//tr')
				for hour in hour_list:
					h_temp += hour.xpath('.//text()')[0] + ' ' + hour.xpath('.//text()')[1] + ', '
				item['store_hours'] = h_temp[:-2]
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					yield item		
		except:
			pass	


	def validate(self, item):
		try:
			return item.strip().replace(';','').replace('&amp;','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

