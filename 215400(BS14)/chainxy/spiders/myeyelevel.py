# from __future__ import unicode_literals
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

class myeyelevel(scrapy.Spider):
	name = 'myeyelevel'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.myeyelevel.com'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("http://www.myeyelevel.com/America/howtostart/findcenter_home.aspx")
		time.sleep(3)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//div[@class="pbdl noM"]//li[@class="rec"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h3/text()')[0])
				detail = store.xpath('.//ul[@class="d"]//li')				
				address = self.validate(detail[0].xpath('.//span/text()')[0])
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
				item['phone_number'] = self.validate(detail[3].xpath('.//span/text()')[0])
				item['store_hours'] = self.validate(detail[6].xpath('./text()')[0]).split(':')[1].strip()
				yield item
			except:
				pdb.set_trace()		
		for cnt in range(0, 22):
			self.driver.find_element_by_id('cpHolder_lbtNext').click()
			time.sleep(3)
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			store_list = tree.xpath('//div[@class="pbdl noM"]//li[@class="rec"]')
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('.//h3/text()')[0])
					detail = store.xpath('.//ul[@class="d"]//li')				
					address = self.validate(detail[0].xpath('.//span/text()')[0])
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
					item['phone_number'] = self.validate(detail[3].xpath('.//span/text()')[0])
					item['store_hours'] = self.validate(detail[6].xpath('./text()')[0]).split(':')[1].strip()
					yield item
				except:
					pass

	def validate(self, item):
		try:
			return item.strip().replace(';',', ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp