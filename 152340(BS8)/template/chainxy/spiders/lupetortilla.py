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

class lupetortilla(scrapy.Spider):
	name = 'lupetortilla'
	domain = 'https://www.lupetortilla.com/'
	history = []

	def start_requests(self):
		init_url = 'https://www.lupetortilla.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@class="see-more hidden-sm hidden-xs"]/@href').extract()
		for store in store_list:
			store = self.domain + store[3:]
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="individual-heading"]//h1/text()').extract_first())
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "address")]//text()').extract())
			item['address'] = detail[0]			
			addr = detail[2].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail[3].split(':')[1])
			h_temp = ''
			for de in detail:
				if 'Phone' not in de and '-' in de:
					if 'am' in de.lower() or 'am' in de.lower():
						h_temp += de +', '
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
