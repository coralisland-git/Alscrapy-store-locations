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

class unclebobsSelfStorage(scrapy.Spider):
	name = 'unclebobsSelfStorage'
	domain = 'https://www.lifestorage.com'
	history = []

	def start_requests(self):
		init_url  = 'https://www.lifestorage.com/storage-units/near-me/'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):		
		state_list = response.xpath('//div[@class="boxExpand"]//li[@class="stateLink"]//a/@href').extract()
		for state in state_list : 
			state_link = self.domain + state
			yield scrapy.Request(url=state_link, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="similarStores"]//div[@class="storesRow"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//strong//a/text()').extract_first()).split('(')[0]
				item['store_number'] = self.validate(store.xpath('.//strong//a/text()').extract_first()).split('#')[1].split(')')[0].strip()
				detail = self.eliminate_space(store.xpath('.//ul//li//text()').extract())
				address = ''
				item['phone_number'] = ''
				for de in detail:
					if 'Phone:' not in de:
						address += de + ', '
					else:
						item['phone_number'] = de.split('Phone:')[1].strip()
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
				yield item			
			except:
				pass

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''