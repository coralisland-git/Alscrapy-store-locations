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

class craftwarehouse(scrapy.Spider):
	name = 'craftwarehouse'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://craftwarehouse.com/'		
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="accordion-item"]//a/@href').extract()
		for store in store_list:
			if 'http' in store:
				yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[contains(@class, "map_inner map-inner")]//h3/text()').extract_first().upper())
			address = self.validate(response.xpath('//div[contains(@class, "map_inner map-inner")]//a/text()').extract_first())
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
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "map_inner map-inner")]//p[1]//text()').extract())
			item['country'] = 'United States'
			for de in detail:
				if '-' in de:
					item['phone_number'] = de
					if 'p:' in de:
						item['phone_number'] = self.validate(de.split('p:')[1])

			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[contains(@class, "map_inner map-inner")]//p[2]/text()').extract())
			for hour in hour_list:
				h_temp += hour.replace('to','-') + ', '
			item['store_hours'] = h_temp[:-2]
			yield item		
		except:
			pass	


	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '-').replace('\xa0', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != ':':
				tmp.append(self.validate(item))
		return tmp