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

class globalpetfoods(scrapy.Spider):
	name = 'globalpetfoods'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.globalpetfoods.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("https://www.globalpetfoods.com/store-locations")
		source = self.driver.page_source.encode("utf8")
		data = source.split('var storeInfos=')[1].split(';var map')[0].strip()
		store_list = data.split('},{')
		for store in store_list[1:]:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store).split('storeName:"')[1].split('",')[0].strip()
				item['address'] = self.validate(store).split('address:"')[1].split('",')[0].strip()
				item['address2'] = self.validate(store).split('address2:"')[1].split('",')[0].strip()
				item['city'] = self.validate(store).split('city:"')[1].split('",')[0].strip()
				item['state'] = self.validate(store).split('province:"')[1].split('",')[0].strip()
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store).split('phone:"')[1].split('",')[0].strip()
				item['latitude'] = self.validate(store).split('lat:')[1].split(',')[0].strip()
				item['longitude'] = self.validate(store).split('lng:')[1].split(',')[0].strip()
				item['store_hours'] = 'monday:' + store.split('monday:')[1].split('}')[0].strip().replace('"','')
				yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('&amp;','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp