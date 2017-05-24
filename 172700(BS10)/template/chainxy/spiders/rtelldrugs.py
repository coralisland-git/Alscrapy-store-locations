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

class rtelldrugs(scrapy.Spider):
	name = 'rtelldrugs'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.bartelldrugs.com/wp-json/api/stores?per_page=100&orderby=title&order=ASC'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['title'])
			item['store_number'] = self.validate(store['number'])
			item['address'] = self.validate(store['address'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['store_phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			item['store_hours'] = 'Store Hours : ' + 'Week ' + self.validate(store['store_hours_week_open']) + '-'+ self.validate(store['store_hours_week_close']) + ', '
			item['store_hours'] += 'Saturday ' + self.validate(store['store_hours_saturday_open']) + '-'+ self.validate(store['store_hours_saturday_close']) + ', '
			item['store_hours'] += 'Sunday ' + self.validate(store['store_hours_sunday_open']) + '-'+ self.validate(store['store_hours_sunday_close']) + ', '
			item['store_hours'] += 'Pharmacy Hours : ' + 'Week ' + self.validate(store['pharmacy_hours_week_open']) + '-'+ self.validate(store['pharmacy_hours_week_close']) + ', '
			item['store_hours'] += 'Saturday ' + self.validate(store['pharmacy_hours_saturday_open']) + '-'+ self.validate(store['pharmacy_hours_saturday_close']) + ', '
			item['store_hours'] += 'Sunday ' + self.validate(store['pharmacy_hours_sunday_open']) + '-'+self.validate(store['pharmacy_hours_sunday_close']) + ', '
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