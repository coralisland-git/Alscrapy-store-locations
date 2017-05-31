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

class miniustorage(scrapy.Spider):
	name = 'miniustorage'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.miniustorage.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table//td')
		for store in store_list:
			store_link = store.xpath('.//a/@href').extract_first()
			if store_link:
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				request = scrapy.Request(url=store_link, callback=self.parse_page)
				request.meta['store_name'] = detail[0]
				address = detail[1] + ' ' + detail[2]
				request.meta['address'] = ''
				request.meta['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						request.meta['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						request.meta['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						request.meta['zip_code'] = temp[0].replace(',','')
					else:
						request.meta['address'] += temp[0].replace(',', '') + ' '
				request.meta['phone_number'] = detail[4]
				yield request

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			item['address'] = response.meta['address']	
			item['city'] = response.meta['city']
			item['state'] = response.meta['state']
			item['zip_code'] = response.meta['zip_code']
			item['country'] = 'United States'
			item['phone_number'] = response.meta['phone_number']
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@id="hours"]//table//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\r','').replace('\t','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp