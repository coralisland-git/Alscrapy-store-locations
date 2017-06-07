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

class davidyurman(scrapy.Spider):
	name = 'davidyurman'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.davidyurman.com/store.html?query=%s&lat=%s&lng=%s&boutique=Y&retailer=Y' %(location['city'], str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body.split('DY.data = ')[1].split('</script>')[0].strip()[:-1])['locations']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['storeName'])
					item['store_number'] = self.validate(store['storeId'])
					item['address'] = self.validate(store['address1'])
					item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zip'])
					item['country'] = self.validate(store['country'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['lat'])
					item['longitude'] = self.validate(store['lng'])
					h_temp = ''
					try:
						hour_list = store['hours']
						for hour in hour_list:
							try:
								h_temp += hour['day'] + ' ' + hour['times'] + ', '
							except:
								pass
						item['store_hours'] = h_temp[:-2]
					except:
						pass
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('<br>','').replace('<i>','').replace('</br>','').replace('</i>','').replace('<br/>','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp
