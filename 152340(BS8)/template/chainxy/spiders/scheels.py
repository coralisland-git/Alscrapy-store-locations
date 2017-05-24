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
import time

class scheels(scrapy.Spider):
	name = 'scheels'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.scheels.com/shop/AjaxProvinceSelectionDisplayView?catalogId=10051&langId=-1&storeId=10151'
		self.header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded',
			'X-Requested-With':'XMLHttpRequest'
		}
		formdata = {
			'countryId':'10001',
			'objectId':'',
			'requesttype':'ajax',
		}
		yield scrapy.FormRequest(url=init_url, headers=self.header, formdata=formdata, method='post', callback=self.parse_state) 

	def parse_state(self, response):
		url = 'http://www.scheels.com/shop/AjaxCitySelectionDisplayView?catalogId=10051&langId=-1&storeId=10151'
		state_list = response.xpath('//select//option/@value').extract()
		for state in state_list:
			try:
				formdata = {
					'provinceId':state,
					'objectId':'',
					'requesttype':'ajax'
				}
				yield scrapy.FormRequest(url=url, headers=self.header, formdata=formdata, method='post', callback=self.parse_city) 
			except:
				pass
		
	def parse_city(self, response):
		url = 'http://www.scheels.com/shop/AjaxStoreLocatorResultsView?catalogId=10051&langId=-1&orderId=&storeId=10151'
		try:
			city_list = response.xpath('//select//option/@value').extract()
			for city in city_list:
				formdata = {
					'cityId':city,
					'fromPage':'',
					'objectId':'',
					'requesttype':'ajax',
					'fromPage':'StoreLocator',
					'geoCodeLatitude':'',
					'geoCodeLongitude':'',
					'errorMsgKey':'',
				}
				yield scrapy.FormRequest(url=url, headers=self.header, formdata=formdata, method='post', callback=self.parse_store) 
		except:
			pdb.set_trace()
	
	def parse_store(self, response):
		try:
			url = response.xpath('//a[@class="button_primary"]/@href').extract_first()
			yield scrapy.Request(url=url, callback=self.parse_page)
		except:
			pass
			

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="left_espot"]//h1/text()').extract_first())
			div_list = response.xpath('//div[@class="left_espot"]//div[contains(@class, "col4 acol12 storedetails_section")]')
			detail = []
			for cnt in range(0, 3):
				data = self.eliminate_space(div_list[cnt].xpath('.//p//text()').extract())
				for da in data:
					detail.append(da)
			address = ''
			h_temp = ''
			for de in detail:
				if ':' in de:
					h_temp += self.validate(de) +', '
				else:
					if '-' in de:
						item['phone_number'] = self.validate(de)
						try:
							check = int(self.validate(de[0:2]))
						except:
							address += self.validate(de) + ', '
					else:
						address += self.validate(de) + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(self.validate(address[:-2]))
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['store_hours'] = self.validate(h_temp[:-2])
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
