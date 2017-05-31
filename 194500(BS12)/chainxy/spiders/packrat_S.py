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

class packrat(scrapy.Spider):
	name = 'packrat1'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'https://www.a1storage.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("https://www.1800packrat.com/locations")
		time.sleep(3)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		# store_list = tree.xpath('//div[@class="store"]')
		# store_list = response.xpath('//a[@class="location-list__city"]')
		# for store in store_list:
		city_list = self.driver.find_elements_by_xpath('//a[@class="location-list__city"]')
		pdb.set_trace()
				# try:
				# 	item = ChainItem()
				# 	item['store_name'] = self.validate(store.xpath('.//h2/text()')[0])
				# 	detail = self.eliminate_space(store.xpath('.//div[@class="addressPhoneInfo"]//text()'))
				# 	item['address'] = detail[0]	
				# 	addr = detail[1].split(',')
				# 	item['city'] = self.validate(addr[0].strip())
				# 	item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				# 	item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				# 	item['country'] = 'United States'
				# 	item['phone_number'] = detail[2]	
				# 	h_temp = ''
				# 	hour_list = self.eliminate_space(store.xpath('.//div[@class="storehours"]//text()'))
				# 	cnt = 1
				# 	for hour in hour_list:
				# 		h_temp += hour + ', '
				# 	item['store_hours'] = h_temp[:-2]
				# 	if item['store_name'] + item['address'] + item['phone_number'] not in self.history:
				# 		self.history.append(item['store_name'] + item['address'] + item['phone_number'])
				# 		yield item	
				# except:
				# 	pass

	def validate(self, item):
		try:
			return item.strip().replace('\t', '').replace('\n',' ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp