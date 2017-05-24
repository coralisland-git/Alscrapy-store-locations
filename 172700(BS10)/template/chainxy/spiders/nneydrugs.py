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

class nneydrugs(scrapy.Spider):
	name = 'nneydrugs'
	domain = 'https://secure.kinneydrugs.com'
	history = []

	def start_requests(self):
		init_url = 'https://secure.kinneydrugs.com/locations.php'
		yield scrapy.Request(url=init_url, callback=self.body) 	

	def body(self, response):
		store_list = response.xpath('//table[@id="locations_list"]//tr//a[1]/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):	
		try:
			detail = self.eliminate_space(response.xpath('//div[@id="contentLocator"]//text()').extract())
			item = ChainItem()
			item['store_name'] = 'Kinney Drugs'
			address = detail[2] + ', ' + detail[3]
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
			item['phone_number'] = detail[5]
			item['store_hours'] = detail[7] + ', ' + detail[8] + ', '
			item['store_hours'] += detail[9] + ' ' + detail[10] + ', ' + detail[11]
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
			if self.validate(item) != '' and self.validate(item) != ':':
				tmp.append(self.validate(item))
		return tmp