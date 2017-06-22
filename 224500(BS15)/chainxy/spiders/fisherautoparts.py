# from __future__ import unicode_literals
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


class fisherautoparts(scrapy.Spider):
	name = 'fisherautoparts'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.fisherautoparts.com/Fisher-Store-Locator.aspx/GetLocations'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/json; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			payload = {
					"lat":str(location['latitude']),
					"lng":str(location['longitude'])
					}
			yield scrapy.Request(url=init_url, body=json.dumps(payload), headers=header, method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = json.loads(response.body.encode("utf8").strip().replace('\u003e','>').replace('\u003c','<'))['d']
			tree = etree.HTML(data)
			store_list = self.eliminate_space(tree.xpath('//text()'))
			for cnt in range(0,len(store_list)/8):
				try:
					item = ChainItem()
					item['store_name'] = store_list[cnt*8]
					item['store_number'] = store_list[cnt*8+1]
					item['address'] = store_list[cnt*8+2]
					item['city'] = store_list[cnt*8+3].split(',')[0]
					item['state'] = store_list[cnt*8+3].split(',')[1]
					item['country'] = 'United States'
					item['phone_number'] = store_list[cnt*8+4]
					item['latitude'] = store_list[cnt*8+6]
					item['longitude'] = store_list[cnt*8+7]
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass
			# try:
			# 	item = ChainItem()
			# 	item['store_name'] = self.validate(store.xpath('.//LocationDesc/text()')[0])
			# 	item['store_number'] = self.validate(store.xpath('.//LocationId/text()')[0])
			# 	item['address'] = self.validate(store.xpath('.//Address/text()')[0])			
			# 	item['city'] = self.validate(store.xpath('.//CityState/text()')[0]).split(' ')[0]
			# 	item['state'] = self.validate(store.xpath('.//CityState/text()')[0]).split(' ')[1]
			# 	item['country'] = 'United States'
			# 	item['phone_number'] = self.validate(store.xpath('.//Phone/text()')[0])
			# 	item['latitude'] = self.validate(store.xpath('.//Latitude/text()')[0])
			# 	item['longitude'] = self.validate(store.xpath('.//Longitude/text()')[0])
			# 	if item['address']+item['phone_number'] not in self.history:
			# 		self.history.append(item['address']+item['phone_number'])
			# 		yield item	
			# except:
			# 	pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and '.com' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp