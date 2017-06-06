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

class naartjiekids(scrapy.Spider):
	name = 'naartjiekids'
	domain = 'http://www.mystore411.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.mystore411.com/store/listing/2209/Naartjie-Kids-store-locations'		
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//td[@class="dotrow"]//a')
		for store in store_list:
			store_name = store.xpath('./text()').extract_first()
			store_link = self.domain + store.xpath('./@href').extract_first()
			yield scrapy.Request(url=store_link, callback=self.parse_page, meta={'store_name':store_name})

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = response.meta['store_name']
			address_list = self.eliminate_space(response.xpath('//span[@itemprop="streetAddress"]//text()').extract())
			a_temp = ''
			for address in address_list:
				a_temp += address + ' '
			item['address'] = self.validate(a_temp)			
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="store-details"]//p[3]/text()').extract())
			for hour in hour_list:
				h_temp += hour + ', '
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