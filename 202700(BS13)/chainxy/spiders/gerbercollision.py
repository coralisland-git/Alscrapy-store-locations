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

class gerbercollision(scrapy.Spider):
	name = 'gerbercollision'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.gerbercollision.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('values:[')[1].strip().split('events:{')[0].strip()[:-2].strip()[:-1]
		store_list = data.split('data:')
		for store in store_list[1:]:
			try:
				store = json.loads(store.split('options:')[0].strip()[:-1])
				item = ChainItem()
				item['store_name'] = self.validate(store['name']) + ' - ' + self.validate(store['brandname'])
				item['store_number'] = self.validate(str(store['id']))
				item['address'] = self.validate(store['address'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['regionname'])
				item['country'] = self.validate(store['country'])
				item['zip_code'] = self.validate(str(store['zip']))
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
				h_temp = ''
				week_list = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
				hour_list = json.loads(self.validate(store['hoursstruct']))
				for cnt in range(0,7):
					try:
						h_temp += week_list[cnt] + ' ' + hour_list[cnt]['START'][0] + '-' + hour_list[cnt]['END'][0] + ', '
					except:
						h_temp += week_list[cnt] + ' ' + 'Closed, '
				item['store_hours'] = h_temp[:-2]
				yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('/','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp