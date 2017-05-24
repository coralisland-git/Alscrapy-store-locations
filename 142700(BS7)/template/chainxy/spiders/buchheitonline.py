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
import pdb

class buchheitonline(scrapy.Spider):
	name = 'buchheitonline'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.buchheitonline.com/locations.aspx'
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, sdch'
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):

		store_list = response.xpath('//table[@style="color: #000000; height: 159px; width: 625px;"]//td')
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			detail = self.eliminate_space(store.xpath('.//text()').extract())
			if 'Office Hours' not in detail:
				try:
					item = ChainItem()
					item['store_name'] = detail[0]
					item['address'] = detail[1]
					addr = detail[2].split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['country'] = 'United States'
					item['phone_number'] = detail[3]
					h_temp = ''
					for cnt in range(5, len(detail)):
						h_temp += detail[cnt] + ', '
					item['store_hours'] = h_temp[:-2]
					yield item			
				except:
					pdb.set_trace()

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