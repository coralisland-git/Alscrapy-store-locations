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

class tillys(scrapy.Spider):
	name = 'tillys'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.tillys.com/storelocator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('var stores = new Array(')[1].strip().split('lat =')[0].strip()[:-2].strip()
		store_list = data.split('new Array(')
		for store in store_list:
			detail = self.eliminate_space(store.split(','))
			if detail:
				try:
					url = 'https://www.tillys.com/store/storehours.jsp?s=%s' %detail[len(detail)-1]
					request = scrapy.Request(url=url, callback=self.parse_page)
					request.meta['latitude'] = detail[0]
					request.meta['longitude'] = detail[1]
					request.meta['store_name'] = detail[2]
					request.meta['store_number'] = detail[len(detail)-1]
					yield request
				except:
					pass

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			item['store_number'] = response.meta['store_number']
			detail = self.eliminate_space(response.xpath('//div[@id="storeLocatorHoursBlock"]//div[2]/span/text()').extract())
			address = ''
			for de in detail:
				if '-' in de:
					item['phone_number'] = de
				else:
					address += de + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
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
			item['latitude'] = response.meta['latitude']
			item['longitude'] = response.meta['longitude']
			h_temp = ''
			hour_list = response.xpath('//table[@id="storeHoursTable"]//tr')
			for hour in hour_list:
				hour = self.eliminate_space(hour.xpath('.//td/text()').extract())
				for temp in hour:
					h_temp += temp.encode('raw-unicode-escape').replace('\xa0', '') + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass	

	def validate(self, item):
		try:
			return item.strip().replace("'",'').replace(')','').replace(';','').replace('\t','').replace('\n','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp