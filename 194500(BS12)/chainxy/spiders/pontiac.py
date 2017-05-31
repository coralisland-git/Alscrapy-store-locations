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

class pontiac(scrapy.Spider):
	name = 'pontiac'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:
			self.US_state_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.mycertifiedservice.com/tools/dealer-locator.extapp.html'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		for location in self.location_list:
			formdata = {
				"searchBy":"cityname",
				"searchValue":location['city'] + ', ' + self.convert_state(location['state']),
				"dealerStateSearchValue":"-1",
				"chosenBrand":"mycertified-service",
				"requestType":"",
				"serviceStatus":"hide",
				"region":self.convert_state(location['state']),
				"province":"",
				"regionName":"",
				"communityName":"",
				"zipCode":"",
				"city":location['city'],
				"dealername":"",
				"tp_gmna-dl":"/dealerlocator/DealerSearch",
				"x-brand":"mycertified-service"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//li[@class="mds-cmp-dealer_information dealer"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//a[contains(@class, "dealername-link")]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//span[@class="street-address"]/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//span[@class="locality"]/text()').extract_first()).split(',')[0].strip()
				item['state'] = self.validate(store.xpath('.//span[@class="locality"]/text()').extract_first()).split(',')[1].strip()
				item['zip_code'] = self.validate(store.xpath('.//span[@class="postal-code"]/text()').extract_first())
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[@class="tel"]/text()').extract_first())
				h_temp = ''
				hour_list = store.xpath('.//div[@class="dealer-openHours vcard"]')
				ti_list = ['Sales Hours: ', 'Service Hours: ', 'Parts Hours: ']
				for ind in range(0,3):
					h_temp += ti_list[ind]
					cnt = 1
					hour = self.eliminate_space(hour_list[ind].xpath('.//text()').extract())
					for ho in hour[1:]:
						h_temp += ho
						if cnt % 2 == 0:
							h_temp += ', '
						else:
							h_temp += ' '
						cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item
			except:
				pass		

	def validate(self, item):
		try:
			return item.strip().replace('\t','').replace('\r','').replace('\n','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def convert_state(self, item):
		for state in self.US_state_list:
			if state['name'].lower() in item.lower():
				return state['abbreviation']
		return ''