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
import pdb

class morfurnitureforless(scrapy.Spider):
	name = 'morfurnitureforless'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.morfurniture.com/storelocator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//li[@class="el-content"]//h4//a')
		for store in store_list:
			title = self.validate(store.xpath('./text()').extract_first())
			store_url = store.xpath('./@href').extract_first()
			yield scrapy.Request(url=store_url, callback=self.parse_page, meta={'title':title})

	def parse_page(self, response):
		store = response.xpath('//div[contains(@class,"info-detail")]//div[@class="box-detail"]')
		item = ChainItem()
		detail = self.eliminate_space(store.xpath('.//p[1]//text()').extract())
		item['store_name'] = self.validate(response.meta['title'])
		address = ''
		for de in detail:
			if 'Address:' not in de:
				address += de + ', '
		item['address'] = ''
		item['city'] = ''
		item['state'] = ''
		addr = usaddress.parse(self.validate(address)[:-2].replace('United State', ''))
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += self.validate(temp[0]).replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] += self.validate(temp[0]) + ' '
			elif temp[1] == 'ZipCode':
				item['zip_code'] = self.validate(temp[0]).replace(',','')
			else:
				item['address'] += self.validate(temp[0]).replace(',', '') + ' '
		item['country'] = 'United States'
		item['phone_number'] = store.xpath('.//p[2]//span//text()').extract_first()
		h_temp = ''
		hour_list = self.eliminate_space(response.xpath('//div[@id="open_hour"]//tr//text()').extract())
		for hour in hour_list:
			h_temp += self.validate(hour)
			if '-' in hour:
				h_temp += ', '
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
