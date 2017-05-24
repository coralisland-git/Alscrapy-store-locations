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

class bigr(scrapy.Spider):
	name = 'bigr'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.bigr.com/LocationEventXML.aspx?zip=&miles=5000&locations=true&events=true&all=true&locType=&country=US'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//Node')	
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//Name/text()'))
			item['store_number'] = self.validate(store.xpath('.//ID/text()'))
			item['address'] = self.validate(store.xpath('.//Address/text()'))
			item['city'] = self.validate(store.xpath('.//City/text()'))
			item['state'] = self.validate(store.xpath('.//State/text()'))
			item['zip_code'] = self.validate(store.xpath('.//Zip/text()'))
			item['country'] = self.validate(store.xpath('.//Country/text()'))
			item['phone_number'] = self.validate(store.xpath('.//Phone/text()'))
			item['latitude'] = self.validate(store.xpath('.//Latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//Longitude/text()'))
			yield item			


	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''