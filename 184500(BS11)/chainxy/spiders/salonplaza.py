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

class salonplaza(scrapy.Spider):
	name = 'salonplaza'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://salonplaza.com/find-a-salon-plaza/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="list-unstyled"]//li//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//section[@class="map"]//p[2]//text()').extract())
			item['store_name'] = detail[0]
			if '(' in detail[2]:
				detail[2] = detail[2].split('(')[0]
			address = detail[1] + ', ' + detail[2]
			if len(detail) == 3 and '-' in detail[2]:
				item['store_name'] = ''
				address = detail[0] + ', ' + detail[1]
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
			p_temp = ''
			for de in detail:
				if '.' in de and len(de) < 15:
					p_temp = de + ', '
				if '-' in de:
					p_temp = de
				if 'Phone:' in de:
					p_temp = self.validate(de.split('Phone:')[1])
			item['phone_number'] = p_temp[:-2]
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