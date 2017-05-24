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
import unicodedata

class bargainhunt(scrapy.Spider):
	name = 'bargainhunt'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.bargainhunt.com/store-locator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("http://www.bargainhunt.com/store-locator")
		time.sleep(2)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		self.driver.find_element_by_xpath('//a[@class="map-arrow"]').click()
		store_list = tree.xpath('//div[@id="tabStores"]//div')
		for cnt in range(1, len(store_list)):
			self.driver.find_element_by_xpath('//div[@id="tabStores"]//div['+str(cnt)+']//a').click()
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			item = ChainItem()
			detail = self.eliminatespace(tree.xpath('//div[@class="info_content"]//p//text()'))
			item['store_name'] = detail[0].replace(':','')
			item['address'] = detail[1]
			addr = detail[2].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = detail[4]
			if 'Hours:' in detail:
				item['store_hours'] = detail[len(detail)-1]
			yield item		
		self.driver.close()

	def eliminatespace(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''