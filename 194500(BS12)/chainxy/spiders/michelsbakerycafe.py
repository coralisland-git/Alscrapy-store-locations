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

class michelsbakerycafe(scrapy.Spider):
	name = 'michelsbakerycafe'
	domain = 'http://www.michelsbakerycafe.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.michelsbakerycafe.com/en/locator/by-province/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store"]//a[1]/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="store-details"]//text()').extract())
			item['store_name'] = detail[0]
			item['address'] = detail[1]		
			addr = detail[2].split(',')
			item['city'] = self.validate(addr[0].strip())
			sz_list = addr[1].strip().split(' ')
			s_temp = ''
			for temp in sz_list[:-2]:
				s_temp += temp + ' '
			item['state'] = self.validate(s_temp)
			z_temp = ''
			for temp in sz_list[-2:]:
				z_temp += temp + ' '
			item['zip_code'] = self.validate(z_temp)
			item['country'] = 'Canada'
			item['phone_number'] = detail[3]
			h_temp = ''
			for de in detail:
				if ':' in de and 'hours' not in de.lower():
					h_temp += de + ', '
			item['store_hours'] = h_temp[:-2]
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