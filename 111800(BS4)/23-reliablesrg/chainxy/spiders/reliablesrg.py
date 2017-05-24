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

class reliablesrg(scrapy.Spider):
	name = 'reliablesrg'
	domain = 'http://www.reliablesrg.com'
	history = []

	def start_requests(self):
		
		init_url = 'http://www.reliablesrg.com/locations.html'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//td[@class="wsite-multicol-col"]')
		for cnt in range(0, len(store_list)):
			data_list = store_list[cnt].xpath('.//text()').extract()
			item = ChainItem()
			if cnt == 0 :
				pass
			else:
				for i in range(0, (len(data_list)-2)/ 5):
					ind = 5 * i
					item['store_name'] = self.validate(data_list[ind+1])
					item['address'] = self.validate(data_list[ind+3])
					address = self.validate(data_list[ind+4]).split(',')
					item['city'] = self.validate(address[0])
					item['state'] = self.validate(address[1].strip().split(' ')[0])
					item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(data_list[2])
					item['store_hours'] = self.validate(data_list[5])
					yield item

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''