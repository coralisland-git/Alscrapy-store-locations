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

class bmoharris(scrapy.Spider):
	name = 'bmoharris'
	domain = ''
	history = []
	site_list = []


	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://branchlocator.bmoharris.com/'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		cnt = 0
		self.driver.get("https://branchlocator.bmoharris.com/")
		for location in self.location_list:
			try:
				self.driver.find_element_by_id('BranchTab').click()
				self.driver.find_element_by_id('inputaddress').send_keys(location['city'])
				self.driver.find_element_by_id('search_button').click()
				time.sleep(3)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//ul[@class="content-list poi-result"]//li[@class="poi-item"]//span[@class="desktopPhone viewBubble"]//a/@href')
				if store_list:
					self.site_list.append(store_list)
				self.driver.find_element_by_id('ATMTab').click()
				time.sleep(2)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//ul[@class="content-list poi-result"]//li[@class="poi-item"]//span[@class="desktopPhone viewBubble"]//a/@href')
				if store_list:
					self.site_list.append(store_list)
			except:
				pass

		for site in self.site_list:
			for link in site:
				yield scrapy.Request(url=link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['address'] = self.validate(response.xpath('//meta[contains(@property, "street_address")]/@content').extract_first())
			item['city'] = self.validate(response.xpath('//meta[contains(@property, "locality")]/@content').extract_first())
			item['state'] = self.validate(response.xpath('//meta[contains(@property,"region")]/@content').extract_first())
			item['zip_code'] = self.validate(response.xpath('//meta[contains(@property, "postal_code")]/@content').extract_first())
			item['country'] = self.validate(response.xpath('//meta[contains(@property, "country_name")]/@content').extract_first())
			item['phone_number'] = self.validate(response.xpath('//meta[contains(@property, "phone_number")]/@content').extract_first())
			item['latitude'] = self.validate(response.xpath('//meta[contains(@property, "latitude")]/@content').extract_first())
			item['longitude'] = self.validate(response.xpath('//meta[contains(@property, "longitude")]/@content').extract_first())
			h_temp = 'Branch Hours: '
			hour_list = self.eliminate_space(response.xpath('//div[@class="branch_hours_inner"]//text()').extract())
			cnt = 1
			for hour in hour_list:
				if cnt == 15:
					h_temp += 'Drive Up: '
				if cnt % 2 == 0:
					if 'closed' not in hour:
						hour = hour.split('-')
						temp = ''
						for ho in hour:
							temp += ho[:2] + ':' + ho[2:] + '-'
						h_temp += temp[:-1] + ', '
					else:
						h_temp += hour + ', '
				else:
					h_temp += hour + ' '
				cnt += 1
			if h_temp == 'Branch Hours: ':
				item['store_hours'] = ''
			else:
				item['store_hours'] = h_temp[:-2]
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
