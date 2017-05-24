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

class fnbbank(scrapy.Spider):
	name = 'fnbbank'
	domain = 'https://www.fnb247.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.fnb247.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = self.eliminate_space(response.xpath('//nav[@class="location_results"]//li//a/@href').extract())
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[@class="first group_1of4"]')
		item = ChainItem()
		item['store_name'] = self.validate(detail.xpath('.//h3/text()').extract_first())
		address_temp = self.eliminate_space(detail.xpath('.//p[1]//text()').extract())
		address = ''
		for temp in address_temp:
			address += temp + ', '
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
		h_temp = ''
		try:
			hour_list = detail.xpath('.//p')
			hour_list_0 = self.eliminate_space(hour_list[len(hour_list)-1].xpath('.//text()').extract())
			for hour in hour_list_0:
				h_temp += hour + ' '
			hour_list_1 = self.eliminate_space(hour_list[len(hour_list)-2].xpath('.//text()').extract())
			h_temp += ', '
			for hour in hour_list_1:
				h_temp += hour + ' '
		except:
			pass
		item['store_hours'] = h_temp
		yield item		

	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp