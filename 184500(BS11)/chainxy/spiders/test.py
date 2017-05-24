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
import time

class test(scrapy.Spider):
	name = 'test'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.woolrich.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		self.driver.get("http://www.woolrich.com/woolrich/storeLocator.jsp?")
		time.sleep(50)
		# self.driver.find_element_by_class_name('viewAllStoresLink').click()
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//div[@class="storeAddressDetails"]')
		print("=========  Checking.......", len(store_list))
		

		# store_list = json.loads(response.body)
		# for store in store_list:
		# 	try:
		# 		item = ChainItem()
		# 		detail = self.eliminate_space(store.xpath())
		# 		item['store_name'] = self.validate(store['name'])
		# 		item['store_number'] = self.validate(store['store_number'])
		# 		item['address'] = self.validate(store['address'])
		# 		item['address2'] = self.validate(store['address2'])
				
		# 		address = ''
		# 		item['address'] = ''
		# 		item['city'] = ''
		# 		addr = usaddress.parse(address)
		# 		for temp in addr:
		# 			if temp[1] == 'PlaceName':
		# 				item['city'] += temp[0].replace(',','')	+ ' '
		# 			elif temp[1] == 'StateName':
		# 				item['state'] = temp[0].replace(',','')
		# 			elif temp[1] == 'ZipCode':
		# 				item['zip_code'] = temp[0].replace(',','')
		# 			else:
		# 				item['address'] += temp[0].replace(',', '') + ' '

		# 		address = ''
		# 		addr = address.split(',')
		# 		item['city'] = self.validate(addr[0].strip())
		# 		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		# 		item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

		# 		item['city'] = self.validate(store['city'])
		# 		item['state'] = self.validate(store['state'])
		# 		item['zip_code'] = self.validate(store['zip'])
		# 		item['country'] = self.validate(store['country'])
		# 		item['phone_number'] = self.validate(store['phone'])
		# 		item['latitude'] = self.validate(store['latitude'])
		# 		item['longitude'] = self.validate(store['longitude'])

		# 		h_temp = ''
		# 		hour_list = ''
		# 		for hour in hour_list:
		# 			h_temp += hour + ', '
		# 		item['store_hours'] = h_temp[:-2]

		# 		item['store_hours'] = self.validate(store['hours'])
		# 		item['store_type'] = ''
		# 		item['other_fields'] = ''
		# 		item['coming_soon'] = ''
		# 		if item['store_number'] not in self.history:
		# 			self.history.append(item['store_number'])
		# 			yield item	
		# 	except:
		# 		pdb.set_trace()		


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

