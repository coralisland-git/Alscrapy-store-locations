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
import time
import unicodedata

class fresh(scrapy.Spider):
	name = 'fresh'
	domain = 'http://www.fresh.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.fresh.com/US/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):	
		data = response.xpath('//script[@type="text/javascript"]')
		dat = unicodedata.normalize('NFKD', data[12].xpath('./text()').extract_first()).encode('ascii','ignore').split('var configuration')[0].split('var stores =')[1].strip()[:-1]		
		store_list = json.loads(dat)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['id']
			item['address'] = store['address1']
			item['address2'] = store['address2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['postalCode']
			item['country'] = store['country']
			item['phone_number'] = store['phone']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			item['store_hours'] = ''
			item['store_type'] = store['storeType']
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item	

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''