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

class qcsupply(scrapy.Spider):
	name = 'qcsupply'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.qcsupply.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[contains(@class, "location-card")]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h3[@class="name"]/text()').extract_first())			
			item['address'] = ''
			item['city'] = ''
			address_temp = self.eliminate_space(store.xpath('.//p[@class="address"]//text()').extract())
			address = ''
			for temp in address_temp:
				address += temp + ', '
			addr = usaddress.parse(address[:-2])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			p_temp = ''
			phone_list = store.xpath('.//p[@class="phone"]//text()').extract()
			for phone in phone_list:
				if '-' in phone:
					p_temp += phone +', '
			item['phone_number'] = p_temp[:-2]
			h_temp = ''
			hour_list = store.xpath('.//div[@class="hours"]//tr')
			for hour in hour_list:
				if self.validate(hour.xpath('.//td[1]/text()').extract_first()) != '':
					h_temp += self.validate(hour.xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour.xpath('.//td[2]/text()').extract_first()).encode('UTF-8') + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			


	def validate(self, item):
		try:
			return item.strip().encode('UTF-8')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
