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

class publix(scrapy.Spider):
	name = 'publix'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)
		proxy_list = [	
					'https://198.50.219.230:8080',
					'https://158.69.223.147:3128',
					'https://167.114.35.69:8080',
					'https://144.217.201.17:8080',
					'https://144.217.189.144:3128',
					'https://144.217.170.87:3128',
					'https://198.50.219.239:80',
					'https://149.56.8.228:8080',
					'https://149.56.201.164:80',
					'https://158.69.31.45:3128'
					]

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://store.publix.com/publix/cgi/selection?mapid=US&lang=en&design=default&region_name=&region=&place='+location['city']+'%2C+'+self.get_state(location['state'])+'&mapx=&mapy='
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate"
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body, meta={'proxy':proxy_list[0]}) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="search_results"]//li[contains(@class, "kwresult_normal")]//a[@class="store-name"]/@href').extract()
		for store in store_list:
			store = 'https:' + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@id="content_2_TitleTag"]/text()').extract_first())
			detail = self.eliminate_space(response.xpath('//div[@class="store-info-group"]//text()').extract())
			item['store_number'] = detail[0].split(':')[1].strip()
			item['address'] = detail[1]		
			addr = detail[2].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = ''
			for de in detail:
				if 'Main:' in de:
					item['phone_number'] = de.split('Main:')[1].strip()
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//li[contains(@id, "content_2_rptSchedule_rptDailySchedule_0_DailySchedule")]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
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
			pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\t','').replace('\n',' ').replace('\r','').replace('\xa0','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def get_state(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['name'].lower() and item != '':
				return state['abbreviation']
		return ''