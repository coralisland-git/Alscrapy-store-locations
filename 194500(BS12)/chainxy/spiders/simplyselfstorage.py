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

class simplyselfstorage(scrapy.Spider):
	name = 'simplyselfstorage'
	domain = 'https://www.simplyss.com'
	history = []
	count = 0
	
	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.simplyss.com/'
		yield scrapy.Request(url=init_url, callback=self.parse_store) 

	def parse_store(self, response):
		store_list = response.xpath('//div[contains(@class, "find-your-spot-locations")]//a/@href').extract()
		for store in store_list : 
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//div[contains(@class, "location-details-box")]//div[@class="row no-margin hidden-xs hidden-sm"]')
			item['store_name'] = self.validate(store.xpath('.//h1[@class="location-name LatoBold"]/text()').extract_first())
			addr_list = self.eliminate_space(store.xpath('.//address/text()').extract())
			address = ''
			for addr in addr_list:
				address += addr
			item['address'] = ''
			item['city'] = ''
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
			item['phone_number'] = self.validate(store.xpath('.//font[@itemprop="telephone"][1]/text()').extract_first()) + '  ' + self.validate(store.xpath('.//font[@itemprop="telephone"][2]/text()').extract_first())
			item['country'] = self.check_country(item['state'])
			h_temp = ''
			hour_list_office = self.eliminate_space(store.xpath('.//div[@class="col-md-6 no-padding-sides"][1]//span//text()').extract())
			if hour_list_office:
				h_temp += 'Office Hours : '
				cnt = 1
				for hour in hour_list_office:
					h_temp += self.validate(hour)
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
			hour_list_gate = self.eliminate_space(store.xpath('.//div[@class="col-md-6 no-padding-sides"][2]//span//text()').extract())
			if hour_list_gate:
				h_temp += 'Gate Hours : '
				cnt = 1
				for hour in hour_list_gate:
					h_temp += self.validate(hour)
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pass

	def check_country(self, item):
		if 'PR' in item.upper():
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if state['abbreviation'] in item.upper():
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
			return item.strip()
		except:
			return ''

	def format(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', unit).strip()
		except:
			return ''