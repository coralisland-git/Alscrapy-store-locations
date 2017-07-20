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
import time
import pdb

class aveda(scrapy.Spider):
	name = 'aveda'
	domain = 'https://www.aveda.com'
	history = []

	def __init__(self, *args, **kwargs):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)


	def start_requests(self):
		init_url = 'https://www.aveda.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		source_list = []
		self.driver.get("https://www.aveda.com/locations")
		time.sleep(1)
		for location in self.location_list:
			try:
				search_form = self.driver.find_element_by_id('store-locator__search')
				search_form.clear()
				search_form.send_keys(location['city'])
				# search_form.send_keys('Houston')
				time.sleep(2)
				self.driver.find_element_by_xpath('//fieldset[@id="store-search-controls"]//button').click()
				time.sleep(3)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//div[@class="sl-tooltip__row sl-tooltip__row--meta"]')
				print('~~~~~~~~~~~~~~~', len(store_list))
				if len(store_list) != 0:
					source_list.append(store_list)
			except:
				pass

		for source in source_list:
			for store in source:
				try:
					item = ChainItem()
					try:
						item['store_name'] = self.eliminate_space(store.xpath('.//span[@class="store_name"]//text()'))[0]
					except:
						pass
					address = self.str_concat(store.xpath('.//div[@class="store-locator__tooltip-address"]//text()'), ', ')
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
					try:
						item['phone_number'] = self.validate(store.xpath('.//a[@class="store-locator__tooltip-phone"]/text()')[0])
					except:
						item['phone_number'] = ''
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pdb.set_trace()		

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "address")]//text()').extract())
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(detail[0])
			addr = detail[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			sz = addr[1].strip().split(' ')
			item['state'] = ''
			item['zip_code'] = self.validate(sz[len(sz)-1])
			for temp in sz[:-1]:
				item['state'] += self.validate(temp) + ' '
			item['phone_number'] = detail[2]
			item['country'] = 'United States'
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[contains(@class, "hours")]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\n',' ').replace('\u2013', '-')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '' and '-' not in self.validate(item):
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp