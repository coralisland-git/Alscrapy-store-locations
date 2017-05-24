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

class jetspizza(scrapy.Spider):
	name = 'jetspizza'
	domain = 'https://jetspizza.com'

	def start_requests(self):
		
		init_url  = 'http://jetspizza.com/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		header = {
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate, sdch',
		}
		state_list = response.xpath('//table[@id="statelist"]//li')
		for state in state_list:
			url = state.xpath('.//a/@href').extract_first()
			link_url = self.domain + url
			yield scrapy.Request(url=link_url, callback=self.parse_page)

	def parse_page(self, response):
		print("==============",response.url)
		store_list = response.xpath('.//div[@class="maincontent"]//table[@id="storesearch"]/tr')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = ''
				item['store_number'] = ''
				address = store.xpath('.//td[1]//text()[2]').extract()
				item['address'] = address[0].strip()
				item['city'] = self.validate(store.xpath('.//td[1]//h2/text()')).split(',')[0].strip()
				item['state'] = self.validate(store.xpath('.//td[1]//h2/text()')).split(',')[1].strip()
				item['zip_code'] = ''
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//a/text()'))
				item['latitude'] = ''
				item['longitude'] = ''
				h_temp = ''
				hour_list = store.xpath('.//table[@class="storehours"]/tr')			
				for hour in hour_list:
					h_temp += self.validate(hour.xpath('.//td[1]/text()')) + ' ' + self.validate(hour.xpath('.//td[2]/text()')) + ', '
				item['store_hours'] = h_temp[:-2]
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				yield item		
			except:
				pass	

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''