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
import time
import usaddress
import pdb

class test(scrapy.Spider):
	name = 'test'
	domain = ''
	history = []
	count = 0

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'https://www.coppel.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("http://www.oribe.com/salon-locator")
		source_list = []
		time.sleep(1)
		self.driver.find_element_by_xpath('//div[@class="modal-close hover-rotate-90"]').click()
		for location in self.US_location_list:
			try:
				search_text = self.driver.find_element_by_xpath('//div[@class="location-search"]//input')
				search_text.clear()
				search_text.send_keys(location['city'])
				time.sleep(1)
				self.driver.find_element_by_xpath('//i[@class="ss-gizmo ss-search"]').click()
				time.sleep(3)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//li[contains(@class, "store")]')
				if store_list:
					source_list.append(store_list)
					self.count += len(store_list)
				print('~~~~~~~~~~~~~~~~~~~', self.count)
			except:
				pass

		# for location in self.CA_location_list:
		# 	try:
		# 		search_text = self.driver.find_element_by_xpath('//div[@class="location-search"]//input')
		# 		search_text.clear()
		# 		search_text.send_keys(location['city'].split('(')[0])
		# 		time.sleep(1)
		# 		self.driver.find_element_by_xpath('//i[@class="ss-gizmo ss-search"]').click()
		# 		time.sleep(3)
		# 		source = self.driver.page_source.encode("utf8")
		# 		tree = etree.HTML(source)
		# 		store_list = tree.xpath('//li[contains(@class, "store featured")]')
		# 		if store_list:
		# 			source_list.append(store_list)
		# 			self.count += len(store_list)
		# 		print('~~~~~~~~~~~~~~~~~~~', self.count)

		# 	except:
		# 		pass

		for source in source_list:
			for store in source:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('.// div[@class="title"]//span//text()')[0].replace('*',''))
					address = self.validate(store.xpath('.//div[@class="address"]/text()')[0])
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
					item['country'] = self.check_country(item['state'])
					try:
						item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]/text()')[0])
					except:
						item['phone_number'] = ''

					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
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
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''