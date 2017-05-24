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

class planetsmoothie(scrapy.Spider):
	name = 'planetsmoothie'
	domain = 'http://www.planetsmoothie.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		
		init_url = 'http://www.planetsmoothie.com/locations-2/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		# with open('response.html', 'wb') as f:
		# 	f.write(response.body)
		store_list = response.xpath('//div[@class="col-md-4 locationcolumn"]')
		for store in store_list:
			item = ChainItem()
			# pdb.set_trace()
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//strong/text()'))
			item['address2'] = ''
			address = self.validate(store.xpath('./text()[2]')).split(',')
			item['city'] = address[0].strip()
			item['state'] = address[1].strip().split(' ')[0].strip()
			item['zip_code'] = address[1].strip().split(' ')[1].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('./div[2]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//div[@class="time_block"]/text()').extract()
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]			
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if item['store_hours'] == '':
				item['coming_soon'] = '1'
			yield item				

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''