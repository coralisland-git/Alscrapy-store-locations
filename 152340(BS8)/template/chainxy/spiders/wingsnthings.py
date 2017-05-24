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

class wingsnthings(scrapy.Spider):
	name = 'wingsnthings'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.epicwingsnthings.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//ul[contains(@class, "location-list")]//li//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//div[contains(@class, "location-data")]//h2/text()').extract_first())
			address_temp = self.eliminate_space(response.xpath('//div[@class="address"]//p//text()').extract())
			address = ''
			for temp in address_temp :
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
			item['phone_number'] = self.validate(response.xpath('//span[@class="address-phone"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="hours"]//p//text()').extract())
			for hour in hour_list:
				if 'a.m.' in hour:
					h_temp += hour + ' , '
			item['store_hours'] = self.validate(h_temp[:-2])
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