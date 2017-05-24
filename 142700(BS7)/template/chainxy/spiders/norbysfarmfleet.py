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

class norbysfarmfleet(scrapy.Spider):
	name = 'norbysfarmfleet'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.norbysfarmfleet.com/locations.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		store_list = response.xpath('//div[@id="store_info_all"]//div[@class="location_entry"]')
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			try:
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item = ChainItem()
				item['address'] = self.validate(detail[1])
				addr = detail[0].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip())
				item['country'] = 'United States'
				item['phone_number'] = detail[3]
				h_temp = ''
				st = 8
				if 'javascript' not in detail[6]:
					st = 6
				for cnt in range(st, len(detail)-2):
					h_temp += detail[cnt]
					if cnt % 2 == 1:
						h_temp += ', '
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
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''