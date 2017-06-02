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
import pdb
import time

class goodyearautoservice(scrapy.Spider):
	name = 'goodyearautoservice'
	domain = 'https://www.goodyearautoservice.com'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.goodyearautoservice.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("https://www.goodyearautoservice.com/en-US/shop")
		time.sleep(1)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		# store_list = tree.xpath('//li[@class="store-results__results__item"]//h4[@class="nav-my-store__store-title"]//a/@href')
		# for store in store_list:
		# 	store = self.domain + store
		# 	yield scrapy.Request(url=store, callback=self.parse_page)
		pagenation = self.driver.find_element_by_class_name('store-results__pagination--next')
		pdb.set_trace()
		pagenation.click()
		source = self.driver.page_source.encode("utf8")
		with open('response.html', 'wb') as f:
			f.write(response.body)
		time.sleep(5)
		# while pagenation:
		# 	pagenation.click()
		# 	time.sleep(1)
		# 	source = self.driver.page_source.encode("utf8")
		# 	tree = etree.HTML(source)
		# 	store_list = tree.xpath('//li[@class="store-results__results__item"]//h4[@class="nav-my-store__store-title"]//a/@href')
		# 	# for store in store_list:
		# 	# 	store = self.domain + store
		# 		# yield scrapy.Request(url=store, callback=self.parse_page)
		# 	pagenation = self.driver.find_element_by_class_name('store-results__pagination--next')


	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//div[@class="store-page-masthead store-page-masthead__wrapper"]')
			item['store_name'] = self.validate(store.xpath('.//span[@itemprop="legalName"]/text()').extract_first())
			item['address'] = self.validate(store.xpath('.//p[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()).split(',')[0].strip()
			item['state'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()).split(',')[1].strip()
			item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//ul[@itemprop="openingHoursSpecification"]//li')
			for hour in hour_list:
				temp = self.eliminate_space(hour.xpath('.//text()').extract())
				for te in temp:
					h_temp += te.strip() + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pdb.set_trace()

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
