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

class lawtons(scrapy.Spider):
	name = 'lawtons'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://lawtons.ca/stores/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('"locations":')[1].strip().split('"homelocation":')[0].strip()[:-1]
		store_list = json.loads(data)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['title'])
				tree = etree.HTML(self.validate(store['description']))
				detail = self.eliminate_space(tree.xpath('//p//text()'))
				item['address'] = self.validate(detail[0])
				addr = detail[1].split(',')
				item['city'] = self.validate(addr[0])
				item['state'] = self.validate(addr[1])[:2]
				item['zip_code'] = self.validate(addr[1])[2:]
				if item['address'] == '107 Catherwood Street, Suite 201':
					print('~~~~~~~~~~~~~~~~~')
					pdb.set_trace()
				item['country'] = 'Canada'
				item['latitude'] = self.validate(store['latitude'])
				item['longitude'] = self.validate(store['longitude'])
				h_temp = ''
				for cnt in range(2, len(detail)):
					if ':' in detail[cnt]:
						h_temp += detail[cnt] + ', '
					else:
						if '-' in detail[cnt]:
							item['phone_number'] = detail[cnt]
				item['store_hours'] = h_temp[:-2]
				yield item			
			except:
				pdb.set_trace()


	def validate(self, item):
		try:
			return item.strip().replace(';','').replace('&amp','-')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp