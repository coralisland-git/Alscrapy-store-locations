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

class deltaco(scrapy.Spider):
	name = 'deltaco'
	domain = 'https://www.deltaco.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded'
		}
		for location in self.location_list:
			form_data = {
				'q':location['city'],
				'distance':'100'
			}
	 		init_url = 'https://www.deltaco.com/index.php?page=locations'
			yield scrapy.FormRequest(url=init_url, method="POST", formdata= form_data, headers=header, callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="locations-list clearfix"]//li')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = ''
				item['store_number'] = ''
				address = store.xpath('.//h3[@class="store-info-location-address body-font black-text"]/text()').extract()
				item['address'] = address[0]
				item['address2'] = ''
				item['city'] = address[1].split(',')[0].strip()
				item['state'] = address[1].split(',')[1].strip().split(' ')[0].strip()
				item['zip_code'] = address[1].split(',')[1].strip().split(' ')[1].strip()
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[contains(@class, "store-info-phone")]//a/text()'))
				geolocation = self.validate(store.xpath('./@data-gmapping'))
				geolocation = json.loads(geolocation)
				item['latitude'] = geolocation['latlng']['lat']
				item['longitude'] = geolocation['latlng']['lng']
				h_temp = ''
				hour_list = store.xpath('.//p[contains(@class, "store-info-hours")]//span/text()').extract()
				for hour in hour_list:
					h_temp += hour + ' '
				item['store_hours'] = h_temp
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['store_name'] + item['phone_number'] in self.history:
					continue
				self.history.append(item['store_name'] + item['phone_number'])
				yield item		
			except:
				pdb.set_trace()	

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''