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

class extremebodysh(scrapy.Spider):
	name = 'extremebodysh'
	domain = 'http://extremebodyshaping.com'
	history = []

	def start_requests(self):
		init_url = 'http://extremebodyshaping.com/find-location'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[contains(@class, "le_content directListingPlace")]//a/@href').extract()
		for state in state_list:
			state_url = self.domain + state
			yield scrapy.Request(url=state_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//div[@class="directory_list_row directory_entry_address"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="entry_name"]//a/text()').extract_first())
			address = store.xpath('.//div[@class="entry_address"]//text()').extract()
			item['address'] = self.validate(address[0])
			if len(address) == 3:
				addr = self.validate(address[1]).split(',')
			else :
				item['address2'] = self.validate(address[1])
				addr = self.validate(address[2]).split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())[:-1]
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = store.xpath('.//div[@class="entry_phone"]/text()').extract_first()
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''