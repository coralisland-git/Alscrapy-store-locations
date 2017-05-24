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

class carinos(scrapy.Spider):
	name = 'carinos'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.carinos.com/Location/Maps?locationType=2'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)
		for store in store_list:
			store = store['Location']
			item = ChainItem()
			item['store_name'] = self.validate(store['LocationName'])
			item['store_number'] = self.validate(str(store['StoreNumber']))
			item['address'] = self.validate(store['Address1'])
			item['address2'] = self.validate(store['Address2'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(store['Zip'])
			item['country'] = self.validate(store['Country'])
			item['phone_number'] = self.validate(store['Phone1'])
			item['latitude'] = self.validate(str(store['Latitude']))
			item['longitude'] = self.validate(str(store['Longitude']))
			item['store_hours'] = self.parse_hours(store['Hours'])
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(';','')
		except:
			return ''

	def parse_hours(self, item):
		item = unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		symbals= ['\r', '\n', '<br>', '<br/>', '<p>', '<ul>','</ul>', '</li>', '<h3>', '</h3>', '<li style="list-style: initial;">']
		for s in symbals:
			item = item.replace(s,'')
		return item