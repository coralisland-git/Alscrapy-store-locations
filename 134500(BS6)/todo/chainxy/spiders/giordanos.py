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
import unicodedata

class giordanos(scrapy.Spider):
	name = 'giordanos'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://giordanos.com/locations/all-locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//ul[@class="poxy txal brown bold _mt2 mt2"]//li//a/@href').extract()
		for state in state_list:
			yield scrapy.Request(url=state, callback=self.parse_page)
		
	def parse_page(self, response):
		store_list = response.xpath('//div[@id="locations_results_wrapper"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h2[contains(@class, "location__name")]//a/text()'))
				item['address'] = self.validate(store.xpath('.//p[contains(@class, "address_1")]/text()'))
				address = store.xpath('.//p[contains(@class, "address_2")]//text()').extract()
				item['city'] = address[0].strip().replace(',','')
				item['state'] = address[1].strip()
				item['zip_code'] = address[2].strip()
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//p[contains(@class, "location__phone poxy")]//a/text()'))
				h_temp = ''
				hour_list = store.xpath('.//div[contains(@class, "location__hours")]//p//text()').extract()
				for hour in hour_list:
					h_temp += hour.strip() +', '
				item['store_hours'] = h_temp[:-2]
				yield item			
			except:
				pass

	def validate(self, item):
		try:
			item = item.extract_first()
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''