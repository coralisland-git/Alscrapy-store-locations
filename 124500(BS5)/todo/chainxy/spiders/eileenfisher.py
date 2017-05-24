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

class eileenfisher(scrapy.Spider):
	name = 'eileenfisher'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.eileenfisher.com/storelocator/Location/search/'
		formdata = {
				'city':'los angeles',
				'region_id':'12',
				'miles':'100',
				'postcode':'',
				'find-domestic':'',
				'country':'US'
			}
		header={
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded'
		}
		yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='POST', callback=self.body) 

	def body(self, response):
		data = response.body.split('var storeData = ')[1].strip().split('var googleMapDivId')[0].strip()[:-1]
		store_list = json.loads(data)
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['store_location'])
			item['store_number'] = self.validate(store['store_code'])
			item['address'] = self.validate(store['street_address1'])
			item['address2'] = self.validate(store['street_address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip_code'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			item['store_type'] = self.validate(store['store_type'])
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''