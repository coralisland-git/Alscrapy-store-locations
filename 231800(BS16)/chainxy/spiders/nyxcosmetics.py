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

class nyxcosmetics(scrapy.Spider):
	name = 'nyxcosmetics'
	domain = 'http://stores.nyxcosmetics.com'
	history = []

	def __init__(self, *args, **kwargs):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://stores.nyxcosmetics.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		source_list = []
		self.driver.get("http://stores.nyxcosmetics.com/en?")
		time.sleep(1)
		# for location in self.location_list:
		search_form = self.driver.find_element_by_id('bwt-q')
		search_form.clear()
		# search_form.send_keys(location['name'])
		search_form.send_keys('California')
		time.sleep(2)
		self.driver.find_element_by_class_name('bwt-index-search-form-submit').click()
		time.sleep(4)
		# try:
		# 	while True:
		# 		more_link = self.driver.find_element_by_id('show_more_link')
		# 		if 'bwt-pagination' not in more_link.get_attribute('class'):
		# 			break;
		# 		more_link.click()
		# except:
		# 	pass
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//ul[@class="bwt-store-list"]//li[@class="bwt-index-store partner-store"]')
		pdb.set_trace()
		print('~~~~~~~~~~~~~~~', len(store_list))
		if store_list:
			source_list.append(store_list)

		for source in source_list:
			for store in source:
				try:
					item = ChainItem()
					try:
						item['store_name'] = self.validate(store.xpath('.//h4[@class="bwt-index-store-body-header-title"]/text()')[0])
					except:
						pass
					address = self.str_concat(store.xpath('.//div[@class="bwt-index-store-body-details-address"]//text()'), ', ')
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
					# try:
					# 	item['phone_number'] = self.validate(store.xpath('.//span[@class="bwt-store-phone-number-link-text"]/text()')[0])
					# except:
					# 	item['phone_number'] = ''
					# h_temp = ''
					# hour_list = self.eliminate_space(store.xpath('.//table[@class="bwt-store-hours-table"]//text()'))
					# cnt = 1
					# for hour in hour_list:
					# 	h_temp += hour
					# 	if cnt % 2 == 0:
					# 		h_temp += ', '
					# 	else:
					# 		h_temp += ' '
					# 	cnt += 1
					# item['store_hours'] = h_temp[:-2]
					if item['address']+item['zip_code'] not in self.history:
						self.history.append(item['address']+item['zip_code'])
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