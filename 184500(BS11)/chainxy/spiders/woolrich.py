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
import time

class woolrich(scrapy.Spider):
	name = 'woolrich'
	domain = ''
	history = []

	def __init__(self):
   		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.woolrich.com/woolrich/storeLocator.jsp'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("http://www.woolrich.com/woolrich/storeLocator.jsp")
		country_list = ['United States', 'Canada']
		# for country in country_list:
		# self.driver.find_element_by_id('country').send_keys('United States')
		# source = self.driver.page_source.encode("utf8")
		# tree = etree.HTML(source)
		# state_list = tree.xpath('//select[@id="state"]//option//text()')
		# # for state in state_list:
		try:
			self.driver.find_element_by_class_name('ltkmodal-close').click()
		except:
			pass
		self.driver.find_element_by_name('state').send_keys('Alaska')
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		city_list = tree.xpath('//select[@id="city"]//option//text()')
		# for city in city_list:
		self.driver.find_element_by_name('city').send_keys('ANCHORAGE')

		self.driver.find_element_by_id('locateStoresBtn').click()
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//div[@class="storeAddressDetails"]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(response.xpath('//div[contains(@class, "address")]//text()').extract())
				item['address'] = detail[0] + ', ' + detail[1]
				addr = detail[2].split(',')
				item['city'] = self.validate(addr[0][:-3])
				item['state'] = self.validate(addr[0][:-3])
				item['zip_code'] = self.validate(addr[1])
				item['phone_number'] = detail[3]
				item['country'] = country
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
