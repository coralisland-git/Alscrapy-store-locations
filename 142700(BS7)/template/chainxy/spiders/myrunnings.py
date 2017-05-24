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

class myrunnings(scrapy.Spider):
	name = 'myrunnings'
	domain = 'http://www.runnings.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.runnings.com/LocationEventMapping.aspx'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="BottomEventListing"]//li[contains(@class, "location-section")]')
		for store in store_list:
			store_name = self.validate(store.xpath('.//a[contains(@class, "location-details")]/@class').extract_first()).split(' ')[1]
			store_url = self.domain + self.validate(store.xpath('.//a[contains(@class, "location-details")]/@href').extract_first())
			yield scrapy.Request(url=store_url, callback=self.parse_page, meta={'store_name':store_name})

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.meta['store_name'])
			address_temp = self.eliminate_space(response.xpath('//div[@id="store-address-hours"]//span[@id="store-address"]//text()').extract())
			address = ''
			for temp in address_temp:
				address += temp + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address[:-2])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@id="store-address-hours"]//p//text()').extract())
			for hour in hour_list:
				if 'am' in hour.lower():
					h_temp += hour + ', '
				if 'Phone' in hour:
					item['phone_number'] = hour		
			item['store_hours'] = h_temp[:-2]
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