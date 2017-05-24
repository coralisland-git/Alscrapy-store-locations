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
import unicodedata
import usaddress

class elsupermark(scrapy.Spider):
	name = 'elsupermark'
	domain = 'http://elsupermarkets.com'
	history = []

	def start_requests(self):
		init_url = 'http://elsupermarkets.com'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//div[@id="catDynMenuSub2326"]//td/@onclick').extract()
		for state in state_list:
			state = state.split('=')[1].strip()[1:-2]
			state_url = self.domain + state + '-stores.html'
			if state == '/el-super-NewMexico':
				state_url = self.domain + state + '.html'
			yield scrapy.Request(url=state_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list_white = response.xpath('//div[@class="white_row_loc"]')
		store_list_grey = response.xpath('//div[@class="grey_row_loc"]')
		store_list = store_list_white + store_list_grey
		for store in store_list:
			try:
				store = store.xpath('.//text()').extract()
				tmp = []
				for st in store:
					if self.validate(st) != '':
						tmp.append(self.validate(st))
				store = tmp
				item = ChainItem()
				item['store_name'] = store[0]
				addr = store[1].split(' ')
				a_temp = ''
				for cnt in range(0, len(addr)-2):
					a_temp += addr[cnt] + ' '
				item['address'] = a_temp.strip().replace(',', '')
				item['state'] = addr[len(addr)-2]
				item['zip_code'] = addr[len(addr)-1]
				c_list = response.url.split('-')
				item['city'] = c_list[len(c_list)-2].strip()
				item['country'] =  'United States'
				item['phone_number'] = store[2].split('/')[0].strip()
				item['store_hours'] = store[2].split('/')[1].strip()
				yield item		
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''