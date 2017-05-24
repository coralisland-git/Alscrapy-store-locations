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

class snipits(scrapy.Spider):
	name = 'snipits'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.snipits.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="loc-result"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//section[@id="hero"]//div[@class="one-third"]//p[1]//text()').extract())
			item['address'] = detail[0]
			if len(detail) == 4:
				addr = detail[2].split(',')
				item['phone_number'] = detail[3]
			else :
				addr = detail[1].split(',')
				item['phone_number'] = detail[2]
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//section[@id="hero"]//div[@class="one-third"]//table//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pass	

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', '').replace('\u2013', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp