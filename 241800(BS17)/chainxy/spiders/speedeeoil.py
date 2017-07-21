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

class speedeeoil(scrapy.Spider):
	name = 'speedeeoil'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.speedeeoil.com/DesktopModules/GITS_StoreLocator/Ajax/Locations.asmx/getLocations'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/json; charset=utf-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		yield scrapy.Request(url=init_url, headers=header, method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['d']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = "SpeeDee Oil Change & Auto Service - Store"
				item['store_number'] = self.validate(store['ShopNumber'])
				item['address'] = self.validate(store['Address'])	
				item['city'] = self.validate(store['City'])
				item['state'] = self.validate(store['State'])
				item['zip_code'] = self.validate(store['Zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['Phone'])
				item['latitude'] = self.validate(store['Latitude'])
				item['longitude'] = self.validate(store['Longitude'])

				h_temp = ''
				hour_list = self.eliminate_space(etree.HTML('<div>'+self.validate(store['Hours'])+'</div>').xpath('//text()'))
				cnt = 1
				for hour in hour_list:
					h_temp += hour
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
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
			if self.validate(item) != '' and 'Store Hours:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp