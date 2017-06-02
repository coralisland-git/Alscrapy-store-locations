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

class tuffy(scrapy.Spider):
	name = 'tuffy'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.tuffy.com/location_search?zip_code='+location['city']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = response.body.split('var locations = [')[1].strip().split('var info_contents')[0].strip()
		geoloc_list = self.eliminate_space(data.split('new google.maps.LatLng('))
		ind = 0
		store_list = response.xpath('//div[@class="contact-info"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h2/text()').extract_first())
				address = self.validate(store.xpath('.//address/text()').extract_first())
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
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[@class="tel"]/text()').extract_first())
				item['latitude'] = self.validate(geoloc_list[ind].split('),')[0].split(',')[0])
				item['longitude'] = self.validate(geoloc_list[ind].split('),')[0].split(',')[1])
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//div[@class="schedule-holder"]//text()').extract())
				cnt = 1
				for hour in hour_list:
					h_temp += hour
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
				ind += 1
			except:
				pass	

	def validate(self, item):
		try:
			return item.replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
