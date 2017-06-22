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

class london(scrapy.Spider):
	name = 'london'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.tedbaker.com/us/json/stores/for-country?isocode=US'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['data']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['displayName'])
				item['store_number'] = self.validate(store['address']['id'])
				address = ''
				try:
					address += self.validate(store['address']['line1'])
				except:
					pass
				try:
					address += ', ' + self.validate(store['address']['line2'])
				except:
					pass
				try:
					address += ', ' + self.validate(store['address']['line3'])
				except:
					pass
				try:
					address += ', ' + self.validate(store['address']['postalCode'])
				except:
					pass
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = self.validate(store['address']['country']['name'])
				try:
					item['phone_number'] = self.validate(store['address']['phone'])
				except:
					pass
				try:
					item['state'] = self.validate(store['address']['region']['name'])
				except:
					pass
				item['latitude'] = self.validate(str(store['geoPoint']['latitude']))
				item['longitude'] = self.validate(str(store['geoPoint']['longitude']))
				try:
					h_temp = ''
					for hour in store['openingHours']['weekDayOpeningList']:
						try:
							h_temp += hour['weekDay'] + ' ' + hour['openingTime']['formattedHour'] + '-' + hour['closingTime']['formattedHour'] + ', '
						except:
							pass
					item['store_hours'] = h_temp[:-2]
				except:
					pass
				yield item	
			except:
				pass

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