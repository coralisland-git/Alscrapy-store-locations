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
import unicodedata

class jeancoutu(scrapy.Spider):
	name = 'jeancoutu'
	domain = 'https://www.jeancoutu.com/'
	history = ['']

	def start_requests(self):
		header = {
		'Accept':'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'en-US,en;q=0.8',
		'Connection':'keep-alive',
		'Content-Length':'0',
		'Content-Type':'application/json; charset=utf-8'
		}
		init_url  = 'https://www.jeancoutu.com/StoreLocator/StoreLocator.svc/LoadStoreInfos'
		yield scrapy.Request(url=init_url, headers=header, method="POST", callback=self.body) 

	def body(self, response):
		print("............. Checking .......")
		with open('re.html', 'wb') as f:
			f.write(response.body)
		store_list = json.loads(response.body)['LoadStoreInfosResult']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.format(store['Store_Name'])
			item['store_number'] = self.format(store['Store'])
			item['address'] = self.format(store['Address_e'])
			item['address2'] = self.format(store['Address_f'])
			item['phone_number'] = store['Front_Phone']
			item['city'] = self.format(store['City'])
			item['state'] = self.format(store['State_Id'])
			item['zip_code'] = store['Zip_Code']
			item['country'] = 'Canada'
			item['latitude'] = store['Latitude']
			item['longitude'] = store['Longitude']
			item['store_hours'] = self.format(store['StoreBusinessHours']) + self.format(store['StoreBusinessHoursException'])
			item['store_type'] = store['StoreType']
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			yield item		

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''