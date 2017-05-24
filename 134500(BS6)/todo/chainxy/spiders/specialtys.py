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
import unicodedata

class specialtys(scrapy.Spider):
	name = 'specialtys'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.specialtys.com/wcf/SpProxy.svc/LoadStores'
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/json; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest'
		}
		yield scrapy.Request(url=init_url, method='post', headers=header, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)['d']
		for store in store_list:
			item = ChainItem()
			item['address'] = self.validate(store['StreetAddress'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(store['Zip'])
			item['country'] = 'United States'
			item['latitude'] = str(store['GpsLat'])
			item['longitude'] = str(store['GpsLong'])
			item['store_hours'] = self.validate(store['FriendlyOpenTimesHtml'])
			item['store_type'] = self.validate(store['LocationType'])
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''