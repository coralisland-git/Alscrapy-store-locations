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

class huhot(scrapy.Spider):
	name = 'huhot'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.huhot.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//a[@class="marker"]/@href').extract()
		for state in state_list:
			yield scrapy.Request(url=state, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = response.xpath('//div[@id="location-content"]')
			item = ChainItem()
			address = detail.xpath('.//div[@class="location-address-block"]//text()').extract()
			tmp =[]
			for addr in address:
				if addr.strip() != '':
					tmp.append(addr.strip())
			address = tmp
			item['store_name'] = self.validate(address[0])
			item['address'] = self.validate(address[1])
			if len(address) == 3:
				item['city'] = self.validate(address[2]).split(',')[0].strip()
				addr_detail = self.validate(address[2]).split(',')[1].strip().split(' ')
			else :
				item['city'] = self.validate(address[3]).split(',')[0].strip()
				addr_detail = self.validate(address[3]).split(',')[1].strip().split(' ')
			state = ''
			for cnt in range(0, len(addr_detail)-1):
				state += addr_detail[cnt] +' '
			item['state'] = state.strip()
			item['zip_code'] = addr_detail[len(addr_detail)-1]
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail.xpath('.//div[@class="location-contact"]//a[1]/text()').extract_first())
			h_temp = ''
			hour_list = response.xpath('//div[@class="location-hours"]//text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '':
					h_temp += self.validate(hour) +', '
			item['store_hours'] = h_temp[:-2]
			yield item		
		except:
			pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''