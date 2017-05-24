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

class nzerpharmacy(scrapy.Spider):
	name = 'nzerpharmacy'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.benzerpharmacy.com/'
		yield scrapy.Request(url=init_url, callback=self.body)

	def body(self, response):
		init_url = 'https://www.benzerpharmacy.com/Contact-Us.aspx/Bindaddress'
		city_list = response.xpath('//div[@class="location_bg_inner"]//a[@class="openadd"]/@id').extract()
		for city in city_list:
			header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/json; charset=UTF-8",
				"X-Requested-With":"XMLHttpRequest"
			}
			payload = {"id":city}
			yield scrapy.Request(url=init_url, body=json.dumps(payload), headers=header, method='post', callback=self.parse_page) 

	def parse_page(self, response):
		store_list = json.loads(response.body)['d']
		store_list = json.loads(store_list)['Addresses']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['pharmacy'])
			item['coming_soon'] ='0'
			if 'Coming' in item['store_name']:
				item['coming_soon'] ='1'
				item['store_name'] = self.validate(item['store_name'].split('(')[0])
			item['store_number'] = self.validate(store['id'])
			item['address'] = self.validate(store['address'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['store_hours'] = self.validate(store['hours'])
			yield item			

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