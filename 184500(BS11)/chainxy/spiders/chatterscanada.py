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

class chatterscanada(scrapy.Spider):
	name = 'chatterscanada'
	domain = 'https://chatters.ca'
	history = []

	def start_requests(self):
		init_url = 'https://chatters.ca/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.body.split('content: ')
		for store in store_list[1:]:
			store = '<div>' + store.split('google.maps.event')[0].strip()[1:-4].strip() + '</div>'
			url = self.domain + etree.HTML(store).xpath('//a/@href')[0]
			yield scrapy.Request(url=url, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1/text()').extract_first())
			detail = self.eliminate_space(response.xpath('//address//text()').extract())
			item['address'] = detail[0]
			if len(detail) == 2:
				addr = detail[0].split(',')
				item['address'] = ''
				for ad in addr[:-2]:
					item['address'] += ad + ', '
				item['city'] = addr[-2]
				item['state'] = addr[-1]
				item['zip_code'] = detail[1]
			elif len(detail) == 4:
				addr = detail[2].split(', ')
				item['city'] = addr[0]
				item['state'] = addr[1]
				item['zip_code'] = detail[3]
			elif len(detail) == 3:
				if ',' in detail[1]:
					addr = detail[1].split(',')
				else:
					addr = detail[1].split(' ')
				item['city'] = self.validate(addr[0])
				item['state'] = self.validate(addr[1])
				item['zip_code'] = detail[2]
			item['country'] = 'Canada'
			phone = self.validate(response.xpath('//ul[@class="store-actions"]//li[1]//a/text()').extract_first())
			if '-' in phone:
				item['phone_number'] = phone
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="block-openingtimes"]//ul//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
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