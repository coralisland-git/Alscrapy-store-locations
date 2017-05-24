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

class pollocampero(scrapy.Spider):
	name = 'pollocampero'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.campero.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table[@class="locations"]//tr')
		for store in store_list:
			try:
				item = ChainItem()
				name = self.validate(store.xpath('.//td[1]//h2/text()').extract_first())
				item['store_name'] = name
				if 'now open' in name.lower() or 'coming' in name.lower():
					item['store_name'] = self.validate(name.split('-')[0])
				detail = store.xpath('.//td[1]//p//text()').extract()
				item['address'] = self.validate(detail[0])
				addr = self.validate(detail[1]).split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				try:
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
				except:
					pass
				item['country'] = 'United States'
				item['coming_soon'] = '1'
				phone = self.validate(store.xpath('.//td[3]//p/text()').extract_first())
				if 'coming soon' not in phone.lower():
					item['phone_number'] = self.validate(phone.split('P:')[1])
					h_temp = ''
					hour_list = store.xpath('.//td[2]//p/text()').extract()
					for hour in hour_list:
						h_temp += self.validate(hour) +', '
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