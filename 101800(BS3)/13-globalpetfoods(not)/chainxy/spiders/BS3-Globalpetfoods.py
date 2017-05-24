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
import pdb

class BS3Globalpetfoods(scrapy.Spider):
	name = 'globalpetfoods1'
	domain = 'https://www.globalpetfoods.com/'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):

		init_url  = 'https://www.globalpetfoods.com/store-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.xpath('//script[@type="text/javascript"]')
		print("=========  Checking.......", len(data))
		# pdb.set_trace()
		self.driver.get("https://www.globalpetfoods.com/store-locations")
		time.sleep(2)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		self.driver.find_element_by_xpath('//ol[@class="results"]//li[1]').click()
		# for store in store_list:
		# 	store_link = self.domain + store

		# store_list = json.loads(response.body)
		# for store in store_list:
		# 	item = ChainItem()
		# 	item['store_name'] = store['name']
		# 	item['store_number'] = store['store_number']
		# 	item['address'] = store['address']
		# 	item['address2'] = store['crossStreet']
		# 	item['city'] = store['city']
		# 	item['state'] = store['state']
		# 	item['zip_code'] = store['zip']
		# 	item['country'] = store['country']
		# 	item['phone_number'] = store['phone']
		# 	item['latitude'] = store['latitude']
		# 	item['longitude'] = store['longitude']
		# 	item['store_hours'] = store['hours']
		# 	item['store_type'] = ''
		# 	item['other_fields'] = ''
		# 	item['coming_soon'] = ''
		# 	if item['store_number'] in self.history:
		# 		continue
		# 	self.history.append(item['store_number'])
		# 	yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''