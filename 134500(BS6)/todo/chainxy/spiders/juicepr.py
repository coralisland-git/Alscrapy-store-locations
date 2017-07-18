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
import unicodedata

class juicepr(scrapy.Spider):
	name = 'juicepr'
	domain = 'https://juicepress.com'
	history = []

	def start_requests(self):
		init_url = 'https://juicepress.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@class="grid-wrapper"]//a/@href').extract()
		for state in state_list:
			state_url = self.domain + state
			yield scrapy.Request(url=state_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//div[contains(@class, "area-item")]//div[@class="item"]')
		for store in store_list:
			item = ChainItem()
			detail = store.xpath('.//h2[@class="alt"]//text()').extract()
			addr = usaddress.parse(detail[1])
			item['address'] = self.validate(detail[0])
			item['city'] = ''
			item['state'] = ''
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += '' + temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			if item['state'] == 'York,':
				item['city'] += ' ' + item['state']
				item['state'] = 'NY'
			if '1296 Madison Ave' in item['address']:
				item['state'] = self.validate(detail[1].strip().split(' ')[1])
				item['zip_code'] = self.validate(detail[1].strip().split(' ')[0])
				item['address'] = item['address'].replace(item['state'],'').replace(item['zip_code'],'')
			h_temp = ''
			hour_list = store.xpath('.//div[@class="hide"]//p//text()').extract()
			cnt = 1
			for hour in hour_list:
				h_temp += self.validate(hour)
				if cnt % 2  == 0:
					h_temp += ', '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''