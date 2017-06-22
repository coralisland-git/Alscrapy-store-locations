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

class superfreshfood(scrapy.Spider):
	name = 'superfreshfood'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.hourscenter.com/superfresh/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//div[@class="states"]//ul[@class="state_list"]//li//a/@href').extract()
		for state in state_list:
			yield scrapy.Request(url=state, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="store_list"]//ul[@class="listing_list"]//li//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]//text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]//text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]//text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//li[@id="iphn"]//a/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//table[@class="hours_list"]//tr//td//text()').extract())
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
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp