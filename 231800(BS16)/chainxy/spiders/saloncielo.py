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

class saloncielo(scrapy.Spider):
	name = 'saloncielo'
	domain = ''
	history = []


	def start_requests(self):
		init_url = 'http://www.saloncielo.com/api/content/render/false/type/xml/query/+structureName:BubblesSalonLocations%20+(conhost:48190c8c-42c4-46af-8d1a-0cd5db894797%20conhost:SYSTEM_HOST)%20+languageId:1*%20+deleted:false%20+live:true%20%20+working:true/orderby/modDate%20desc/limit/50'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.body.split('<content>')
		for store in store_list[1:]:
			try:
				item = ChainItem()
				item['store_name'] = self.parse_data(store, 'salonName')
				item['store_number'] = self.parse_data(store, 'salonNo')
				item['address'] = self.parse_data(store, 'address')
				item['city'] = self.parse_data(store, 'city')
				item['state'] = self.parse_data(store, 'state')
				item['zip_code'] = self.parse_data(store, 'zipCode')
				item['country'] = 'United States'
				item['phone_number'] = self.parse_data(store, 'phone')
				item['latitude'] = self.parse_data(store, 'latitude')
				item['longitude'] = self.parse_data(store, 'longitude')
				item['store_hours'] = self.parse_data(store, 'storeHours')[1:-1].replace('=',' ')
				yield item	
			except:
				pass

	def parse_data(self, item, param):
		try:
			return item.split('<'+param+'>')[1].split('</'+param+'>')[0].strip()
		except:
			return ''

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp