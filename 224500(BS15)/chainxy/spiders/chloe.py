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

class chloe(scrapy.Spider):
	name = 'chloe'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.chloe.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['post_title'])
				item['store_number'] = self.validate(str(store['ID']))
				try:
					item['address'] = self.validate(store['wpcf-yoox-store-geolocation-address'])
				except:
					item['address'] = ''
				try:
					item['city'] = self.validate(store['location']['city']['name'])
				except:
					item['city'] = ''
				try:
					item['zip_code'] = self.validate(store['wpcf-yoox-store-zip'])
				except:
					item['zip_code'] = ''
				try:
					item['country'] = self.validate(store['location']['country']['name'])
				except:
					item['country'] = ''
				try:
					item['phone_number'] = self.validate(store['wpcf-yoox-store-phone'])
				except:
					item['phone_number'] = ''
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				try:
					item['store_hours'] = self.validate(store['wpcf-yoox-store-hours'])
				except:
					pass
				try:
					item['address'] = item['address'].replace(item['city'], '').replace(item['zip_code'], '').replace(',','').replace(item['country'], '')
				except:
					pass

				if item['country'] == 'United States of America':
					item['state'] = item['zip_code'].split(' ')[0].strip()
					item['zip_code'] = item['zip_code'].split(' ')[1].strip()
				if item['country'] == 'United States':
					item['state'] = item['address'].strip()[-2:]
					item['address'] = item['address'].strip()[:-2]
				if item['country'] == 'Canada':
					if len(item['zip_code']) > 7:
						item['state'] = item['zip_code'][:2].strip()
						item['zip_code'] = item['zip_code'][2:].strip()
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('\xe9', '').replace(';',', ').replace('\xa0','').replace('|', ' ').replace('\n','').replace('\t','').replace('\r','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
