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

class deserrescanada(scrapy.Spider):
	name = 'deserrescanada'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.deserres.ca/en/find-a-store'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//li[@class="store"]//a[@class="shop-arrow"]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="location"]//address//text()').extract())
			item['city'] = self.validate(response.xpath('//div[@class="location"]//h4/text()').extract_first())
			if len(detail) == 3:
				item['address'] = self.validate(detail[0].split('(')[0])
				item['state'] = self.validate(detail[0].split('(')[1]).replace('(','').replace(')','')
				if len(item['state']) > 20:
					item['state'] = self.validate(detail[0].split('(')[2]).replace('(','').replace(')','')
				item['zip_code'] = self.validate(detail[1])
				item['phone_number'] = self.validate(detail[2])
			elif len(detail) == 4 or len(detail) == 6:
				item['address'] = self.validate(detail[0])
				try:
					item['state'] = self.validate(detail[1]).split('(')[1].replace(')', '')
				except:
					item['state'] = self.validate(detail[1]).replace('(','').replace(')','')
				item['zip_code'] = self.validate(detail[2])
				item['phone_number'] = self.validate(detail[3])
			elif len(detail) == 5:
				item['address'] = self.validate(detail[0])
				item['state'] = self.validate(detail[2]).replace('(','').replace(')','')
				item['zip_code'] = self.validate(detail[3])
				item['phone_number'] = self.validate(detail[4])
			item['country'] = 'Canada'
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//dl//text()').extract())
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
			return item.strip().replace('\n','').replace('\r','').replace('\t','').replace('  ', '')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp