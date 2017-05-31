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

class greatamericancookies(scrapy.Spider):
	name = 'greatamericancookies'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.greatamericancookies.com/locations/'		
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[@class="locations"]//li//div[@class="result-content"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h2[contains(@class, "location-name")]//a/text()').extract_first())
			addr_list = self.eliminate_space(store.xpath('.//h3[contains(@class, "location-address")]//span//text()').extract())
			address = ''
			for addr in addr_list:
				address += addr + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address[:-2])
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
			item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]//a/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(store.xpath('.//div[@class="hours"]//text()').extract())
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = '0'
			if 'coming' in item['store_hours'].lower():
				item['coming_soon'] = '1'
				item['store_hours'] = ''
			yield item			

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', '').strip().replace('\n', '').replace('\r', '')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp