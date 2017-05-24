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

class coastalfarm(scrapy.Spider):
	name = 'coastalfarm'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.coastalfarm.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=500&radius=100' %(str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['store'])
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['zip'])
				item['country'] = self.validate(store['country'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				h_temp = ''
				hour_list = etree.HTML('<div>'+self.validate(store['hours'])+'</div>').xpath('//div//text()')
				cnt = 0
				for hour in hour_list:
					h_temp += self.validate(hour)
					if cnt % 2 == 1:
						h_temp += ', '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['phone_number'] not in self.history:
					self.history.append(item['phone_number'])
					yield item			
		except:
			pass


	def validate(self, item):
		try:
			return item.strip().replace(';', '')
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