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

class schlotzskys(scrapy.Spider):
	name = 'schlotzskys'
	domain = 'https://www.schlotzskys.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest'
		}
		init_url  = 'https://www.schlotzskys.com/find-your-schlotzskys/'
		for location in self.location_list:
			form_data = {
					'search[search]':location['city']
				}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=form_data, method="POST", callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="each-result"]')
		for store in store_list:
			url = self.validate(store.xpath('.//div[@class="fixed-items"]//a[contains(@href, "https")]/@href'))
			yield scrapy.Request(url=url, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		store = response.xpath('//div[@class="container locations-mid-container"]')
		item['store_name'] = ''
		item['store_number'] = ''
		item['address'] = self.validate(store.xpath('.//div[@class="locations-address"]/text()'))
		item['address2'] = self.validate(store.xpath('.//div[@class="locations-address-secondary"]/text()'))
		address = self.validate(store.xpath('.//div[@class="locations-state-city-zip"]/text()'))
		item['city'] = address.split(',')[0].strip()
		item['state'] = address.split(',')[1].strip().split(' ')[0].strip()
		item['zip_code'] = address.split(',')[1].strip().split(' ')[1].strip()
		item['country'] = 'United States'
		item['phone_number'] = self.validate(store.xpath('.//div[@class="locations-phone-fax"]//a/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		item['store_hours'] = self.validate(store.xpath('.//div[@class="locations-hours"]//div[@class="locations-hours-time"]/text()'))
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		if item['phone_number'] not in self.history:
			self.history.append(item['phone_number'])
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace(';',', ')
		except:
			return ''