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

class raleys(scrapy.Spider):
	name = 'raleys'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.raleys.com/www/storelocator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="cms_content_frame"]//table//table[2]//td[@class="main-body"]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['store_name'] = detail[0]
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(detail[1])
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0]
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',', '')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = 'United States'
				ph_temp = detail[2].split('|')
				for ph in ph_temp:
					if 'Hours:' in ph:
						item['store_hours'] = self.validate(ph.split('Hours:')[1])
					else:
						if '-' in ph:
							item['phone_number'] = ph
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