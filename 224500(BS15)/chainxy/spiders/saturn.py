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

class saturn(scrapy.Spider):
	name = 'saturn'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)
		self.kind_list = ['chevrolet', 'gmc', 'cadillac', 'buick']

	def start_requests(self):
		init_url = 'http://www.mycertifiedservice.com/tools/dealer-locator.extapp.html'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		for location in self.location_list:
			for kind in self.kind_list:
				formdata = {
					"searchBy":"cityname",
					"searchValue":"",
					"dealerStateSearchValue":"-1",
					"chosenBrand": kind,
					"requestType":"",
					"serviceStatus":"hide",
					"region":self.get_state(location['state']),
					"province":"",
					"regionName":"",
					"communityName":"",
					"zipCode":"",
					"city":location['city'].upper(),
					"dealername":"",
					"tp_gmna-dl":"/dealerlocator/DealerSearch",
					"x-brand":"mycertified-service",
					"renderChosenBrand":"true",
					"chosenCity":location['city'].upper() + ', ' + self.get_state(location['state'])  
				}
				yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//ul[@id="mds-cmp-dealer_list"]//li[@class="mds-cmp-dealer_information dealer"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//a[@class="dealername-link"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//span[@class="street-address"]/text()').extract_first())
				try:
					item['city'] = self.validate(store.xpath('.//span[@class="locality"]/text()').extract_first()).split(',')[0].strip()
					item['state'] = self.validate(store.xpath('.//span[@class="locality"]/text()').extract_first()).split(',')[1].strip()
				except:
					pass
				item['zip_code'] = self.validate(store.xpath('.//span[@class="postal-code"]/text()').extract_first())
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[@class="tel"]/text()').extract_first())
				h_temp = ''
				hour_list = store.xpath('.//div[@class="dealer-openHours vcard"]')
				for hour in hour_list:
					data = self.eliminate_space(hour.xpath('.//text()').extract())
					cnt = 1
					temp = data[0] + ' '
					for ho in data[1:]:
						temp += ho
						if cnt % 2 == 0:
							temp += ', '
						else:
							temp += ' '
						cnt += 1
					h_temp += temp
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('\r','').replace('\n','').replace('\t','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''

	def get_state(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''
