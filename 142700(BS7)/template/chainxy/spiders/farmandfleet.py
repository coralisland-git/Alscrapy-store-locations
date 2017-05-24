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

class farmandfleet(scrapy.Spider):
	name = 'farmandfleet'
	domain = 'https://www.farmandfleet.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.farmandfleet.com/stores/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "sl-see-details")]//a[@class="sl-details-link"]/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		store = response.xpath('//div[@class="store-list-detail"]')
		item['store_name'] = self.validate(response.xpath('.//div[@class="store-details-section"]//h1/text()').extract_first())
		address_temp = self.eliminate_space(store.xpath('.//div[@class="sl-address"]//text()').extract())
		address = ''
		for temp in address_temp:
			address += temp +', '
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(address)
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += temp[0].replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] = temp[0]
			elif temp[1] == 'ZipCode':
				item['zip_code'] = temp[0].replace(',','')
			else:
				item['address'] += temp[0].replace(',', '') + ' '
		item['country'] = 'United States'
		item['phone_number'] = self.validate(store.xpath('.//a[@itemprop="telephone"]/text()').extract_first())
		h_temp = ''
		hour_list = store.xpath('.//div[contains(@class, "sl-store-hours")]//div[@class="sl-hours"]')
		for hour in hour_list:
			hour = self.eliminate_space(hour.xpath('.//div/text()').extract())
			for h in hour:
				h_temp += h +' '
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

