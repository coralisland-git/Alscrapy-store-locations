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

class firstchoicehaircutters(scrapy.Spider):
	name = 'firstchoicehaircutters'
	domain = 'http://www.firstchoice.com/customer/salonlocatorbrowse/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.firstchoice.com/customer/salonlocatorbrowse/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@id="result_StateList"]//li/@onclick').extract()
		for state in state_list:
			state = self.validate(state.split('location=')[1][1:-1])
			url = self.domain + state
			yield scrapy.Request(url=url, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//div[@id="result_CityList"]//li/@onclick').extract()
		for city in city_list:
			city = self.validate(city.split('location=')[1][1:-1])
			url = self.domain + city
			yield scrapy.Request(url=url, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="result_MoreInfo"]//a/@href').extract()
		for store in store_list:
			url = 'http://www.firstchoice.com' + store
			yield scrapy.Request(url=url, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@id="detailA"]/text()').extract())
			name_list = self.eliminate_space(response.xpath('//div[@id="detailA_Salon"]/text()').extract())
			n_temp = ''
			for name in name_list:
				n_temp += name + ' '
			item['store_name'] = self.validate(n_temp)
			item['address'] = detail[0]
			addr = detail[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			sz = addr[1].strip().split(' ')
			item['state'] = sz[0]
			item['zip_code'] = ''
			for temp in sz[1:]:
				item['zip_code'] += temp + ' '
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = self.validate(detail[2])
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@id="detailC"]//text()').extract())
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass	

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', ' ').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'