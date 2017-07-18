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

class northshorefarms(scrapy.Spider):
	name = 'northshorefarms'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://northshorefarms.com/contact-us/'
		yield scrapy.Request(url=init_url, callback=self.body) 
	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//div[@class="indent1"]//table')
		name_list = self.eliminate_space(response.xpath('//div[@class="indent1"]//h3//text()').extract())
		for ind in range(0, len(store_list)):
			try:
				item = ChainItem()
				detail = self.eliminate_space(store_list[ind].xpath('.//text()').extract())
				item['store_name'] = name_list[ind]
				address = detail[3]
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
				item['phone_number'] = detail[1]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass	

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\r',
				'')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp