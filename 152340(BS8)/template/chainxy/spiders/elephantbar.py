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

class elephantbar(scrapy.Spider):
	name = 'elephantbar'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.elephantbar.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('"places":')[1].strip().split('"styles":')[0].strip()[:-1]
		store_list = json.loads(data)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['title'])
			item['address'] = self.validate(store['address']).split(',')[0]
			item['city'] = self.validate(store['location']['city'])
			item['state'] = self.validate(store['location']['state'])
			item['zip_code'] = self.validate(store['location']['postal_code'])
			item['country'] = self.validate(store['location']['country'])
			item['phone_number'] = self.validate(store['location']['extra_fields']['phone'])
			item['latitude'] = self.validate(store['location']['lat'])
			item['longitude'] = self.validate(store['location']['lng'])
			item['store_hours'] = 'Mon-Thur' + self.validate(store['location']['extra_fields']['schedule-mon-thur']) + ', '
			item['store_hours'] += 'Friday' + self.validate(store['location']['extra_fields']['schedule-friday']) + ', '
			item['store_hours'] += 'Saturday' + self.validate(store['location']['extra_fields']['schedule-saturday']) + ', '
			item['store_hours'] += 'Sunday' + self.validate(store['location']['extra_fields']['schedule-sunday'])
			yield item			

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