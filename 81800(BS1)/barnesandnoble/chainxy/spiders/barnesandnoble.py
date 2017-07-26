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

class barnesandnoble(scrapy.Spider):
	name = 'barnesandnoble'
	domain = 'http://stores.barnesandnoble.com'
	history = ['']
	count = 0
	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		self.cnt = 0			
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				'Accept-Encoding':'gzip, deflate',
			}
		for location in self.location_list	:
			init_url = 'http://stores.barnesandnoble.com/stores?lng='+str(location['longitude'])+'&lat='+str(location['latitude'])+'&searchText='+location['city']+'%2c+'+self.get_state(location['state'])+'&storeFilter=all&view=list'
			yield scrapy.Request(url=init_url, headers=header, callback=self.parse_pagenation) 
		# yield scrapy.Request(url='http://stores.barnesandnoble.com/stores?page=0&size=10&lng=-121.9499568&lat=37.2871651&searchText=Campbell%2c+CA&storeFilter=all&view=list&v=1', headers=header, callback=self.parse_pagenation) 

	def parse_pagenation(self, response):
		pagenation_list = []
		temp_list = response.xpath('//div[@class="col-sm-12 col-md-12 col-lg-12 col-xs-12"][1]//a[contains(@href, "/stores")]')
		for temp in temp_list:
			value = self.validate(temp.xpath('./text()').extract_first())
			if 'next' not in value.lower():
				temp_url = self.domain + self.validate(temp.xpath('./@href').extract_first())
				pagenation_list.append(temp_url)
		# pdb.set_trace()
		# if len(pagenation_list) > 1:			
		# 	first = pagenation_list[0].replace('page=1','page=0')			
		# 	pagenation_list.append(first)
		try:
			store_list = response.xpath('.//div[@class=" col-md-7 col-lg-7 col-sm-7 col-xs-7"]')
			for store in store_list:
				detail_link = self.domain+store.xpath('.//a[1]/@href').extract_first()	
				yield scrapy.Request(url=detail_link, callback=self.parse_detail)
		except:
			pass

		for pagenation in pagenation_list:
			yield scrapy.Request(url=pagenation, callback=self.parse_body)

	def parse_body(self, response):
		try:
			store_list = response.xpath('.//div[@class=" col-md-7 col-lg-7 col-sm-7 col-xs-7"]')
			for store in store_list:
				detail_link = self.domain+store.xpath('.//a[1]/@href').extract_first()	
				yield scrapy.Request(url=detail_link, callback=self.parse_detail)
		except:
			pass	

	def parse_detail(self, response):
		data = response.xpath('//div[@class="col-sm-8 col-md-4 col-lg-4 col-xs-6"]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(data.xpath('.//h4/text()').extract_first().strip())
			item['store_number'] = ''
			address= data.xpath('./text()').extract()
			item['address'] = self.validate(address[2])
			item['address2'] = ''
			item['city'] = self.validate(address[3].strip().split(',')[0])
			item['state'] = self.validate(address[3].strip().split(',')[1].strip().split(' ')[0])
			item['zip_code'] = self.validate(address[3].strip().split(',')[1].strip().split(' ')[1])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(address[4].strip())
			item['store_hours'] = self.validate(data.xpath('.//div//h4/text()').extract_first()) + ' ' + self.validate(data.xpath('.//div//div/text()').extract_first())
			if item['store_name']+str(item['store_number']) not in self.history:
				self.history.append(item['store_name']+str(item['store_number']))
				yield item
		except:
			item = ChainItem()
			item['store_name'] = self.validate(data.xpath('.//h4/text()').extract_first())
			item['store_number'] = ''
			address= data.xpath('./text()').extract()
			item['address'] = self.validate(address[1])
			item['address2'] = ''
			item['city'] = self.validate(address[2].strip().split(',')[0])
			item['state'] = self.validate(address[2].strip().split(',')[1].strip().split(' ')[0])
			item['zip_code'] = self.validate(address[2].strip().split(',')[1].strip().split(' ')[1])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(address[4].strip())
			item['store_hours'] = self.validate(data.xpath('.//div//h4/text()').extract_first())+ ' ' + self.validate(data.xpath('.//div//div/text()').extract_first())
			if item['store_name']+str(item['store_number']) not in self.history:
				self.history.append(item['store_name']+str(item['store_number']))
				yield item

	def validate(self,item):
		try:
			return item.strip()
		except:
			return ''			
	def get_state(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''