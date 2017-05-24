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
import pdb
import unicodedata

class bashassupermarkets(scrapy.Spider):
	name = 'bashassupermarkets'
	domain = 'http://www.bashas.com/Pharmacy/PharmacyLocator.aspx?'
	history = []

	def start_requests(self):
		init_url = 'http://www.bashas.com/Pharmacy/PharmacyLocator.aspx?'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		city_list = response.xpath('//select[@name="ctl00$mainBodyArea$ddlLocations"]//option/@value').extract()
		for city in city_list:
			city_url = self.domain + 'city=' +city
			yield scrapy.Request(url=city_url, callback=self.parse_page)

	def parse_page(self, response):
		store_list = response.xpath('//table//tr')
		for cnt in range(0, len(store_list)/5):
			try:
				item = ChainItem()
				cnt = cnt * 5
				detail = store_list[cnt+1].xpath('.//td[1]//text()').extract()
				detail = self.eliminatespace(detail)
				item['store_name'] = detail[0]
				item['address'] = detail[2]
				addr = detail[3].split(',')
				item['city'] = self.validate(addr[0])
				sz_temp = self.eliminatespace(addr[1].strip().split(' '))
				item['state'] = sz_temp[0]
				item['zip_code'] = sz_temp[1]
				item['country'] = 'United States'
				hour_list = store_list[cnt+1].xpath('.//td[2]//text()').extract()
				hour_list = self.eliminatespace(hour_list)
				h_temp = ''
				for cnt in range(1,len(hour_list)-2):
					h_temp += hour_list[cnt] + ', '
				item['store_hours'] = h_temp[:-2]
				item['phone_number'] = hour_list[len(hour_list)-1]
				yield item	
			except:
				pass		

	def eliminatespace(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip().replace(';','').replace('\n', '').replace('\t','').replace('\r', '')
		except:
			return ''