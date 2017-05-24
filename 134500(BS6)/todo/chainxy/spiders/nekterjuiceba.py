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

class nekterjuiceba(scrapy.Spider):
	name = 'nekterjuiceba'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://momentfeed-prod.apigee.net/api/llp.json?auth_token=YFPOHLGEBGSKZZOW&pageSize=100'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			store = store['store_info']
			item['store_name'] = self.validate(store['name'])
			item['coming_soon'] = '0'
			if 'Coming Soon' in item['store_name']:
				item['store_name'] = item['store_name'].split('-')[0].strip()
				item['coming_soon'] = '1'
			item['store_number'] = self.validate(store['corporate_id'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address_extended'])
			item['city'] = self.validate(store['locality'])
			item['state'] = self.validate(store['region'])
			item['zip_code'] = self.validate(store['postcode'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			h_temp = ''
			week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			hour_list = self.validate(store['store_hours']).split(';')
			for hour in hour_list:
				try:
					hour = hour.split(',')
					h_temp += week_list[int(hour[0])-1] + ' ' + hour[1][:2] + ':' + hour[1][2:]
					h_temp += '-' + hour[2][:2] + ':' + hour[2][2:] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''