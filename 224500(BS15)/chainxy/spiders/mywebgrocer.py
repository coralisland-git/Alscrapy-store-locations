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

class mywebgrocer(scrapy.Spider):
	name = 'mywebgrocer'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://starmarket.mywebgrocer.com/Stores/Get?Country=United%20States&Region=Massachusetts&StoreType=Cir&StoresPageSize=undefined&IsShortList=undefined&_=1498069601669'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="storelist-inner-tab"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h4/text()').extract_first())
				detail = self.eliminate_space(store.xpath('.//p//text()').extract())
				address = ''
				for de in detail:
					if 'phone' in de.lower():
						item['phone_number'] = de.split(':')[1].strip()
						break
					address += de + ', '
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address[:-2])
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
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('.//div[@id="StoreServicesContainer"]//span//text()').extract())
				for hour in hour_list:
					h_temp += hour + ', '
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