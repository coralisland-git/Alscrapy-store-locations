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
import pdb

class minuteclinic(scrapy.Spider):
	name = 'minuteclinic'
	domain = 'https://www.cvs.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'https://www.cvs.com/minuteclinic/clinic-locator'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 
		# yield scrapy.Request(url='https://www.cvs.com/minuteclinic/clinic-locator/clinicdetails.jsp?storeId=4795&_requestid=382962#', callback=self.parse_page)

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="states-wrap"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_city)	

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="city-wrap"]//a/@href').extract()
		for city in city_list :
			city_link = self.domain + city
			yield scrapy.Request(url=city_link, callback=self.parse_store)
		
	def parse_store(self, response):
		store_list = response.xpath('//div[contains(@class, "clinics-results")]//a/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			addr_list = self.eliminate_space(response.xpath('//div[@class="dBox01"][1]//text()').extract())[1:]
			address = ''
			for addr in addr_list:
				if 'locate' in addr.lower() or 'corner' in addr.lower() or 'shop' in addr.lower() or 'null' in addr.lower() or 'intersection' in addr.lower() or 'market' in addr.lower():
					addr = self.validate(addr.split(',')[0])
				address += addr + ', '
			item['address'] = ''
			item['city'] = ''
			item['state'] = ''
			addr = usaddress.parse(address[:-2])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = self.check_country(item['state'])
			h_temp = 'MinuteClinic hours: '
			hour_list = self.eliminate_space(response.xpath('//div[@class="dMarginBot2"][1]/text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour + ', '
				if cnt == 3:
					h_temp += 'Lunch hours: '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				if item['address'] != '':
					yield item			
		except:
			pass

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.replace('\n','').replace('\t','').replace('\r',' ').replace('  ',' ').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != ''and 'shopping' not in self.validate(item).lower() and 'set' not in self.validate(item).lower() and 'myClinic' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp