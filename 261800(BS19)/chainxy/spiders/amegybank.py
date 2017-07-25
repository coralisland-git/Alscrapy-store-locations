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

class amegybank(scrapy.Spider):
	name = 'amegybank'
	domain = 'https://www.branchspot.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.branchspot.com/json/map-markers/?t=1&i=4031'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			detail = etree.HTML(store['infoWindowContent'])
			url = self.domain + detail.xpath('//a/@href')[0]
			request = scrapy.Request(url=url, callback=self.parse_page)
			request.meta['store_name'] = detail.xpath('//span[@class="map-info-window-subtitle"]//a/text()')[0]
			request.meta['address'] = detail.xpath('//td[@class="map-info-window-data"]//text()')[0]
			request.meta['phone_number'] = detail.xpath('//td[@class="map-info-window-data"]//text()')[1]
			request.meta['latutude'] = self.validate(str(store['marker']['lat']))
			request.meta['longitude'] = self.validate(str(store['marker']['lng']))
			yield request

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = response.meta['store_name']
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(response.meta['address'])
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
		item['phone_number'] = response.meta['phone_number']
		item['latitude'] = response.meta['latutude']
		item['longitude'] = response.meta['longitude']
		h_temp = ''
		hour_list = response.xpath('//table[@class="hours-table"]//tr')
		for hour in hour_list:
			h_temp += self.validate(hour.xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour.xpath('.//td[2]/text()').extract_first()) + ', '
		item['store_hours'] = h_temp[:-2]
		yield item			

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