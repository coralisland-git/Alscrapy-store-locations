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

class doubletree(scrapy.Spider):
	name = 'doubletree'
	domain = ''
	history = []

	def start_requests(self):
		regionId_list = ['414', '415', '416', '417', '418']
		for regionId in regionId_list:
			init_url = 'http://doubletree3.hilton.com/en_US/dt/ajax/cache/regionHotels.json?regionId='+regionId+'&subregionId=null&hotelStatus=null'
			header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['hotels']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['name'])
					item['address'] = self.validate(store['address1'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zip'])
					item['country'] = self.validate(store['country'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(str(store['lat']))
					item['longitude'] = self.validate(str(store['lng']))
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item				
				except:
					pass	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''
