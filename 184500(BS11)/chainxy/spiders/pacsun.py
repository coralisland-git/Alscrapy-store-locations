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

class pacsun(scrapy.Spider):
	name = 'pacsun'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.pacsun.com/stores'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		print("=========  Checking.......")
		for location in self.location_list:
			self.driver.get("http://www.pacsun.com/stores")
			self.driver.find_element_by_id('dwfrm_storelocator_maxdistance').send_keys('100 Miles')
			self.driver.find_element_by_id('dwfrm_storelocator_address_states_stateUSStoreLocator').send_keys(location['name'])
			self.driver.find_element_by_name('dwfrm_storelocator_findbystate').click()
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			store_list = tree.xpath('//div[@class="store"]')
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('.//h2/text()')[0])
					detail = self.eliminate_space(store.xpath('.//div[@class="addressPhoneInfo"]//text()'))
					item['address'] = detail[0]	
					addr = detail[1].split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['country'] = 'United States'
					item['phone_number'] = detail[2]	
					h_temp = ''
					hour_list = self.eliminate_space(store.xpath('.//div[@class="storehours"]//text()'))
					cnt = 1
					for hour in hour_list:
						h_temp += hour + ', '
					item['store_hours'] = h_temp[:-2]
					if item['store_name'] + item['address'] + item['phone_number'] not in self.history:
						self.history.append(item['store_name'] + item['address'] + item['phone_number'])
						yield item	
				except:
					pass

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