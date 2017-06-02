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

class lubefast(scrapy.Spider):
	name = 'lubefast'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.lubefast.com/wp-content/plugins/store-locator/sl-xml.php'
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, sdch",
				}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//marker')	
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('./@name')).split('#')[0].strip()
			item['store_number'] = self.validate(store.xpath('./@name')).split('#')[1].strip()
			item['address'] = self.validate(store.xpath('./@street'))
			item['address2'] = self.validate(store.xpath('.//@street2'))
			item['city'] = self.validate(store.xpath('.//@city'))
			item['state'] = self.validate(store.xpath('.//@state'))
			item['zip_code'] = self.validate(store.xpath('.//@zip'))
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//@phone'))
			item['latitude'] = self.validate(store.xpath('.//@lat'))
			item['longitude'] = self.validate(store.xpath('.//@lng'))
			item['store_hours'] = self.validate(store.xpath('.//@hours'))
			item['coming_soon'] = '0'
			if 'am' in item['phone_number']:
				temp = item['phone_number']
				item['phone_number'] = item['store_hours']
				item['store_hours'] = temp
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('Phone:', '').replace('&#44;',' , ').replace('&#39;', "'").replace('&amp;','&').replace(';', '').replace(' to ','-')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
