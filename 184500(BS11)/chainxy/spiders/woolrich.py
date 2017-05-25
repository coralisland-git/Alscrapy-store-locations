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
import pdb

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
		for country in country_list:
			self.driver.find_element_by_id('country').send_keys(country)
			try:
				self.driver.find_element_by_class_name('ltkmodal-close').click()
			except:
				pass
			time.sleep(1)
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			state_list = tree.xpath('//select[@id="state"]//option//text()')
			for state in state_list[1:]:
				self.driver.find_element_by_name('state').send_keys(state)
				try:
					self.driver.find_element_by_class_name('ltkmodal-close').click()
				except:
					pass
				time.sleep(1)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				city_list = tree.xpath('//select[@id="city"]//option//text()')
				for city in city_list[1:]:
					self.driver.find_element_by_name('city').send_keys(city)
					try:
						self.driver.find_element_by_class_name('ltkmodal-close').click()
					except:
						pass	
					time.sleep(1)
					self.driver.find_element_by_id('locateStoresBtn').click()
					time.sleep(1)
					source = self.driver.page_source.encode("utf8")
					tree = etree.HTML(source)
					store_list = tree.xpath('//div[@class="storeAddressDetails"]')
					for store in store_list:
						try:
							item = ChainItem()
							detail = self.eliminate_space(store.xpath('.//text()'))
							item['store_name'] = detail[0]
							item['address'] = detail[1]
							addr = detail[2].split(',')
							item['city'] = self.validate(addr[0][:-2])
							item['state'] = self.validate(addr[0][-2:])
							item['zip_code'] = self.validate(addr[1])
							item['phone_number'] = detail[3]
							item['country'] = country
							yield item
						except:
							pdb.set_trace()

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xc2', '').replace('\xa0', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp
