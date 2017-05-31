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

class californiaarizonastoragecenters(scrapy.Spider):
	name = 'californiaarizonastoragecenters'
	domain = 'https://www.castorage.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.castorage.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = response.xpath('//a[@class="header-city-location"]/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[@class="fac-info"]//h1/text()').extract_first())
			addr_list = self.eliminate_space(response.xpath('//div[@class="fac-info"]//li[1]//text()').extract())
			address = ''
			for addr in addr_list:
				address += addr + ' '
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
			try:
				item['phone_number'] = self.validate(response.xpath('//div[@class="fac-info"]//li[2]//a/text()').extract_first()).split('Call Now :')[1].strip()
			except:
				pass
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@id="hours"]//ul//text()').extract())
			for hour in hour_list:
				h_temp += hour + ' '
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = response.url
			if item['store_name'] == '':
				store_list = response.xpath('//a[contains(@id, "select_item_2")]/@href').extract()
				for store in store_list:
					store_link = self.domain + store
					yield scrapy.Request(url=store_link, callback=self.parse_page)
			else:
				yield item
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('  ','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp