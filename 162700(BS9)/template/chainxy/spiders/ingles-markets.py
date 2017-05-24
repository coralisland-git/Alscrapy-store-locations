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

class inglesmarkets(scrapy.Spider):
	name = 'ingles-markets'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.ingles-markets.com/store_locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		url = 'http://www.ingles-markets.com/store_locations/search.php'
		state_list = self.eliminate_space(response.xpath('//select[@id="state"]//option/@value').extract())
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded",
		}
		for state in state_list:
			formdata = {
				"zip":"",
				"radius":"10",
				"zip_order_by":"distance",
				"city":"",
				"state":state,
				"Submit":"Find My Ingles Store"
			}
			yield scrapy.FormRequest(url=url, method='POST', formdata=formdata, headers=header, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//table//tr//a[1]/@href').extract()
		for store in store_list:
			if 'map' in store:
				store = "http://www.ingles-markets.com/store_locations/" + store
				yield scrapy.Request(url=store, callback=self.parse_detail)

	def parse_detail(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//fieldset//div[2]//span[1]//strong/text()').extract_first())
			address = self.validate(response.xpath('//fieldset//div[2]//span[2]//strong/text()').extract_first())
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = self.validate(temp[0])[:-1]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			detail = self.eliminate_space(response.xpath('//fieldset//div[2]/text()').extract())
			item['phone_number'] = ''
			for de in detail:
				if ':' in de:
					item['store_hours'] = self.validate(de).replace('to', '-')
				else:
					if '-' in de:
						item['phone_number'] = self.validate(de)
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''
