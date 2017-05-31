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

class winchellsdonuthouse(scrapy.Spider):
	name = 'winchellsdonuthouse'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://winchells.com/'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("https://www.bullseyelocations.com/pages/qnfembed?f=1")
		time.sleep(1)
		for location in self.location_list:
			time.sleep(5)
			self.driver.find_element_by_name('ctl00$ContentPlaceHolder1$txtCityStateZip').clear()
			self.driver.find_element_by_name('ctl00$ContentPlaceHolder1$txtCityStateZip').send_keys(location['city']+','+location['state'])
			self.driver.find_element_by_name('ctl00$ContentPlaceHolder1$radiusList').send_keys('50 mi')
			self.driver.find_element_by_name('ctl00$ContentPlaceHolder1$searchButton').click()
			time.sleep(5)
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			try:
				store_list = tree.xpath('//ul[@id="resultsCarouselWide"]//li[contains(@class, "jcarousel-item jcarousel-item-vertical")]//div[@class="resultsDetails"]')
				for store in store_list:
					try:
						item = ChainItem()
						item['store_name'] = self.validate(store.xpath('.//h3[@itemprop="name"]/text()')[0])
						item['address'] = self.validate(store.xpath('.//span[@itemprop="streetAddress"]/text()')[0])
						item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()')[0])[:-1]
						item['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]/text()')[0])
						item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()')[0])
						item['country'] = 'United States'
						item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()')[0])
						item['latitude'] = self.validate(store.xpath('.//meta[@itemprop="latitude"]/@content')[0])
						item['longitude'] = self.validate(store.xpath('.//meta[@itemprop="longitude"]/@content')[0])
						item['store_hours'] = self.validate(store.xpath('.//meta[@itemprop="openingHours"]/@content')[0])
						if item['address']+item['phone_number'] not in self.history:
							self.history.append(item['address']+item['phone_number'])
							yield item	
					except:
						pass
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
