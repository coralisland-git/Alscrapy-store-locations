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
import pdb
import tokenize
import token
from StringIO import StringIO

class bluecoastburrito(scrapy.Spider):
	name = 'bluecoastburrito'
	domain = ''
	history = []
	cnt = 0
	def start_requests(self):
		init_url = 'http://bluecoastburrito.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//div[contains(@class, "et_pb_column et_pb_column_1_3")]')
 		for store in store_list:
 			url = store.xpath('.//a[contains(@class, "et_pb_promo_button et_pb_button")]/@href').extract_first()
 			if self.validate(url) != '' :
				yield scrapy.Request(url=url, callback=self.parse_page)
			else:
				try:
					detail = self.eliminate_space(store.xpath('.//div[@class="et_pb_promo_description"]//text()').extract())
					item = ChainItem()
					item['store_name'] = detail[0]
					item['address'] = detail[1]
					try:
						addr = detail[2].split(',')
						if len(addr) == 2:
							item['city'] = self.validate(addr[0].strip())
							item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
							item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
						else:
							item['city'] = self.validate(addr[0].strip())
							item['state'] = self.validate(addr[1].strip())
							item['zip_code'] = self.validate(addr[2].strip())
						item['country'] = 'United States'
					except:
						pass
					item['coming_soon'] = '1'
					yield item
				except:
					pass

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="header-content"]//text()').extract())
			item['store_name'] = detail[0]
			address = detail[1].split('|')
			item['address'] = self.validate(address[0])
			try:
				addr = address[1].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				item['phone_number'] = self.validate(address[2])
			except:
				pass
			item['country'] = 'United States'
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[contains(@class,"et_pb_text et_pb_module et_pb_bg_layout_dark et_pb_text_align_left")]//text()').extract())
			for hour in hour_list:
				if 'am' in hour.lower() and 'pm' in hour.lower():
					h_temp += self.validate(hour) + ', '
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = '0'
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
