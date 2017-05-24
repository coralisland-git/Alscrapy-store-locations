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
import pdb
import tokenize
import token
from StringIO import StringIO

class caffeartigianocanada(scrapy.Spider):
	name = 'caffeartigianocanada'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.caffeartigiano.com/pages/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//ul[@class="tabs-content"]//li')
		for state in state_list:
			title_list = state.xpath('.//h3/text()').extract()
			for cnt in range(0, len(title_list)):
				detail = self.eliminate_space(state.xpath('.//table['+str(cnt+1)+']//text()').extract())
				item = ChainItem()
				item['store_name'] = self.validate(title_list[cnt])
				item['address'] = detail[0]
				addr = detail[1].split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip()[:2])
				item['zip_code'] = self.validate(addr[1].strip()[:2])
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(detail[2])
				h_temp = ''
				for de in detail:
					if ':' in de:
						h_temp += de + ', '
				item['store_hours'] = h_temp[:-2]
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