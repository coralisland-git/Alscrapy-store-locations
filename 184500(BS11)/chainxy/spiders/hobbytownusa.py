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

class hobbytownusa(scrapy.Spider):
	name = 'hobbytownusa'
	domain = 'https://www.hobbytown.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.hobbytown.com/ajax/store-locations/state-list'
		header = {
			"accept":"*/*",
			"accept-encoding":"gzip, deflate, br",
			"content-type":"application/x-www-form-urlencoded; charset=UTF-8",
			"x-requested-with":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"country":"223",
				"state":location['abbreviation']
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		store_list = response.xpath('//table//tr//a[@class="profile"]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		print("=========  Checking.......")
		try:
			item = ChainItem()
			address_temp = self.eliminate_space(response.xpath('//div[@class="address"]//text()').extract())
			address = ''
			for temp in address_temp:
				address += temp + ', '
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
			item['phone_number'] = self.validate(response.xpath('//div[@class="phone"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="hours"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			if item['address'] != '':
				yield item	
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
