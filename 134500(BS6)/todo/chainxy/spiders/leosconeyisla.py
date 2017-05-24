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

class leosconeyisla(scrapy.Spider):
	name = 'leosconeyisla'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.leosconeyisland.com/Locations/tabid/59/Default.aspx'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="dnn_ctr386_ModuleContent"]//table[2]//tr//td')
		for store in store_list:
			try:
				item = ChainItem()
				store = store.xpath('.//text()').extract()
				tmp = []
				for st in store:
					if st.strip() != '':
						tmp.append(st.strip())
				store = tmp
				item['store_name'] = self.validate(store[0])
				item['address'] = self.validate(store[1])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store[2])
				h_temp = ''
				for cnt in range(4, len(store)):
					h_temp += self.validate(store[cnt]) + ', '
				item['store_hours'] = h_temp[:-2]
				yield item		
			except:
				pass	

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''