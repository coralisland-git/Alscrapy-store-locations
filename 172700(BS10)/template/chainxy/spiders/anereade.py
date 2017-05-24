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

class anereade(scrapy.Spider):
	name = 'anereade'
	domain = 'http://reviewrx.com'
	history = []

	def start_requests(self):
		init_url = 'http://reviewrx.com/duane-reade-locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//div[@class="chainpage_text"]//li//a/@href').extract()
		for state in state_list:
			state = self.domain + state
			yield scrapy.Request(url=state, callback=self.parse_pagenation)

	def parse_pagenation(self, response):
		store_list = response.xpath('//div[@id="searchpagecontent-wrap"]//span[@class="searchpage_listing"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

		if response.xpath('//a[@class="page larger"]') is not None:
			for cnt in range(1, 23):
				url = 'http://reviewrx.com/search/?pp='+str(cnt)+'&sc=duane-reade&sl=New+York'
				yield scrapy.Request(url=url, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@id="searchpagecontent-wrap"]//span[@class="searchpage_listing"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = response.xpath('//div[@class="singlepost_text"]//ul//li')
			item = ChainItem()
			item['store_name'] = self.validate(detail[0].xpath('./text()').extract_first())
			address_temp = self.eliminate_space(detail[0].xpath('.//a//text()').extract())
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
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			temp = self.eliminate_space(detail[1].xpath('.//text()').extract())
			for te in temp:
				if 'Number' in te:
					item['phone_number'] = self.validate(te.split('Number')[1])
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