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

class rubytuesday(scrapy.Spider):
	name = 'rubytuesday'
	domain = 'https://www.rubytuesday.com/'
	history = ['']
	country = ''
	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'http://www.rubytuesday.com/locations'
		franchise_url = 'https://www.rubytuesday.com/franchise'
		for location in self.location_list:
			data = '------WebKitFormBoundary3O6JYZuU2T2J4z3v Content-Disposition: form-data; name="address" '+location['city']+' ------WebKitFormBoundary3O6JYZuU2T2J4z3v--'
			yield scrapy.Request(url=init_url, body=data, method='POST', callback=self.body) 
		
		yield scrapy.Request(url=franchise_url, callback=self.parse_frenchise)			

	def body(self, response):		
		pagenation = response.xpath('.//ul[@class="pages"]//li//a[@rel="next"]')
		store_list = response.xpath('.//div[@class="restaurant-location-item clearfix"]')

		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="titleWrap micro clearfix"]//h1/text()').extract_first())
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//address[@class="restaurant-location-address micro"]/text()').extract_first())
			item['address2'] = ''
			address = self.eliminate_space(store.xpath('.//address[@class="restaurant-location-address micro"]/text()').extract())
			item['city'] = self.validate(address[1].split(',')[0].strip())
			item['state'] = self.validate(address[1].split(',')[1].strip()[0:2])
			item['zip_code'] = self.validate(address[1].split(',')[1].strip()[-5:])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//a[@class="phone micro"]/text()').extract_first())
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//table//tr')
			for hour in hour_list:
				h_temp = h_temp + self.validate(store.xpath('.//td[1]/text()').extract_first()) + ' ' +self.validate(store.xpath('.//td[2]/text()').extract_first()) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if item['phone_number'] not in self.history:
				yield item
				self.history.append(item['phone_number'])
		
		if pagenation is not None:
			page_url = pagenation.xpath('./@href').extract_first()
			try:
				yield scrapy.Request(url=page_url, callback=self.body)
			except:
				pass

	def parse_frenchise(self, response):
			
		store_list = response.xpath('//div[@class="franchise-intl-locations-left"]//p')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//strong/text()').extract_first())
				item['store_number'] = ''
				address = store.xpath('./text()').extract()
				if len(address) == 5 :
					item['address'] = address[1]
					item['address2'] = address[2]
					item['city'] = self.validate(address[3].split(',')[0])
					item['country'] = self.validate(address[3].split(',')[1])
					item['phone_number'] = self.validate(address[4].split(':')[1])
				elif len(address) == 4 :
					item['address'] = address[1]
					item['address2'] = ''
					item['city'] = self.validate(address[2].split(',')[0])
					item['country'] = self.validate(address[2].split(',')[1])
					item['phone_number'] = self.validate(address[3].split(':')[1])
				elif len(address) == 6:
					item['address'] = self.validate(address[1]) + self.validate(address[2])
					item['address2'] = self.validate(address[3])
					item['city'] = self.validate(address[4].split(',')[0])
					item['country'] = self.validate(address[4].split(',')[1])
					item['phone_number'] = self.validate(address[5].split(':')[1])
				else :
					item['address'] = self.validate(address[1]) + self.validate(address[2])
					item['address2'] = self.validate(address[3]) + self.validate(address[4])
					item['city'] = self.validate(address[5].split(',')[0])
					item['country'] = self.validate(address[5].split(',')[1])
					item['phone_number'] = self.validate(address[6].split(':')[1])
				item['latitude'] = ''
				item['longitude'] = ''
				item['store_hours'] = ''
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = '0'
				if item['phone_number'] not in self.history:
					yield item
					self.history.append(item['phone_number'])
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