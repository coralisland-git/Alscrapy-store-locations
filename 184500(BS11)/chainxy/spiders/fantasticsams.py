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

class fantasticsams(scrapy.Spider):
	name = 'fantasticsams'
	domain = 'https://www.fantasticsams.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.state_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.fantasticsams.com/find-salon?field_salon_address_country=US&field_salon_address_administrative_area='+self.get_state(location['state'])+'&field_salon_address_locality='+location['city']+'&field_geofield_distance[country]=US'
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, sdch, br"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[@class="view-content"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="title"]/text()').extract_first())
			address = self.validate(response.xpath('//div[@class="salon-address-thoroughfare"]/text()').extract_first())
			address += ', ' + self.validate(response.xpath('//div[@class="salon-address-city-state-zip"]/text()').extract_first())
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
			item['phone_number'] = self.validate(response.xpath('//div[contains(@class, "views-field-field-salon-phone")]//a/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//div[contains(@class, "views-field-php")]//span[@class="oh-display"]')
			for hour in hour_list:
				temp = hour.xpath('.//text()').extract()
				for te in temp:
					h_temp += te
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
		except:
			pass

	def get_state(self, item):
		for state in self.state_list:
			if item in state['name']:
				return state['abbreviation']
		return ''

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

	