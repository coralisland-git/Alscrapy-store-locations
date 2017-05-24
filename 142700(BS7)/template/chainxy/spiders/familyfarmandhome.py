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
import tokenize
import token
from StringIO import StringIO

class familyfarmandhome(scrapy.Spider):
	name = 'familyfarmandhome'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.familyfarmandhome.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list =response.xpath('//ul[@class="locations"]//li[@class="location selected-location"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h4/text()').extract_first())
			detail = self.eliminate_space(store.xpath('.//ul[@class="list-contacts"]//text()').extract())
			item['address'] = self.validate(detail[0])
			addr = detail[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail[len(detail)-1])
			item['store_hours'] =self.validate(detail[3]).replace('NOW OPEN!,', '').strip()
			yield item			


	def validate(self, item):
		try:
			return item.strip().replace('\r',', ').replace('\n', '').replace('|', ', ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
