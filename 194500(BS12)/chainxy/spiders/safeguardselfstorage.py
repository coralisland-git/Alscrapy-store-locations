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

class safeguardselfstorage(scrapy.Spider):
	name = 'safeguardselfstorage'
	domain = 'https://www.safeguardit.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.safeguardit.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//footer//ul[@class="list-inline"]//a/@href').extract()
		for state in state_list:
			state = self.domain + state
			yield scrapy.Request(url=state, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="grid-item"]//h4[@class="clearfix"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			n_temp = ''
			name_list = self.eliminate_space(response.xpath('//h2[@class="brand-name"]//text()').extract())
			for name in name_list:
				n_temp += name + ' '
			item['store_name'] = self.validate(n_temp)
			addr_list = self.eliminate_space(response.xpath('//address//text()').extract())
			address = ''
			for addr in addr_list:
				address += addr + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address[:-2])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['phone_number'] = self.eliminate_space(response.xpath('//p[@class="phone-number"]//text()').extract())[1].split('(')[1].strip().split(',')[0].strip()[1:-1]
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="list-hours"][1]//text()').extract())
			for hour in hour_list:
				h_temp += self.format(hour) + ', '
			item['store_hours'] = self.validate(h_temp[:-2])
			yield item
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def format(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', '').strip()
		except:
			return ''


	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp