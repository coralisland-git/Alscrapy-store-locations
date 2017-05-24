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

class sleephappens(scrapy.Spider):
	name = 'sleephappens'
	domain = 'https://www.sleephappens.com/'
	history = []

	def start_requests(self):
		header = {
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate, br',
			'Accept-Language':'en-US,en;q=0.8',
			'Connection':'keep-alive',
			'Content-Length':'0',
			'Content-Type':'application/json; charset=utf-8'
		}
		init_url  = 'http://www.sleephappens.com/storelocator/index/loadstore/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def parse_page(self, response):
		detail = response.xpath('//div[@class="store-locator-view-detail"]')
		item = ChainItem()
		item['store_name'] = self.validate(detail.xpath('.//div[@class="store-locator-item-name"]//font/text()'))
		item['store_number'] = ''
		address = detail.xpath('.//span[1]//p')
		item['address'] = self.validate(address[0].xpath('./text()'))
		item['address2'] = ''
		print('~~~~~~~~~~~~~~~~~``',self.validate(address[1].xpath('./text()')) )
		item['city'] = self.validate(address[1].xpath('./text()')).split(',')[0].strip()	
		item['state'] = self.validate(address[1].xpath('./text()')).split(',')[1].strip().split('  ')[0].strip()
		item['zip_code'] = self.validate(address[1].xpath('./text()')).split(',')[1].strip().split('  ')[1].strip()
		item['country'] = self.validate(address[2].xpath('./text()'))
		item['phone_number'] = self.validate('.//span[2]//p/text()')
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = detail.xpath('.//div[@id="open_hour"][1]//ul/li')
		for hour in hour_list:
			for time in hour.xpath('.//div'):
				h_temp += self.validate(time.xpath('./text()')) + ' '
			h_temp += ', '		
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item			

	def body(self, response):

		store_list = response.xpath('//li[@class="item"]')
		for store in store_list:
			detail_url = self.validate(store.xpath('.//p[@class="store_detail"]//a/@href'))	
			yield scrapy.Request(url=detail_url, callback=self.parse_page)	

	def validate(self, item):
		try:
			item = item.extract_first().strip()
			item = unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
			return item
		except:
			return ''

	