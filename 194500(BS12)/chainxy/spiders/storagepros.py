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
import pdb

class storagepros(scrapy.Spider):
	name = 'storagepros'
	domain = 'https://www.cubesmart.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		for location in self.location_list:
			state = location['state'].replace(' ','-')
			city = location['city'].replace(' ','-')
			init_url = 'https://www.cubesmart.com/'+state+'-self-storage/'+city+'-self-storage/'
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@class="csUnitButton csGreenButton"]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['address'] = self.validate(response.xpath('//p[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//p[@class="csHoursList"][1]//text()').extract())
			if hour_list:
				h_temp += 'Office Hours '
				for hour in hour_list:
					h_temp += hour + ', '
			hour_list = self.eliminate_space(response.xpath('//p[@class="csHoursList"][2]//text()').extract())
			if hour_list:
				h_temp += 'Storage Gate Hours '
				for hour in hour_list:
					h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
		except:
			pdb.set_trace()		

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