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

class racebros(scrapy.Spider):
	name = 'racebros'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'https://www.racebros.com/'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("https://www.racebros.com/contact")
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//div[@class="c2inlineContent"]//div[@class="txtNew"]')
		h_temp = self.eliminate_space(store_list[5].xpath('.//text()'))[0].split('stores')[1].strip().replace('or',',')
		for store in store_list[1:4]:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()'))
				item['store_name'] = detail[0]
				address = detail[1] + ',' + detail[2]
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
				item['phone_number'] = detail[3]
				item['store_hours'] = h_temp
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
