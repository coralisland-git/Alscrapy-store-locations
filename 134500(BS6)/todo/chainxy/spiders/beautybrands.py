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
import unicodedata

class beautybrands(scrapy.Spider):
	name = 'beautybrands'
	domain = 'https://www.beautybrands.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.beautybrands.com/store-locator/all-stores.do'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[@class="eslStore ml-storelocator-headertext"]//a/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		detail = response.xpath('//div[@class="ml-storelocator-details-col-1"]')
		item['store_name'] = self.validate(detail.xpath('.//div[@class="eslStore"]/text()'))
		item['address'] = self.validate(detail.xpath('.//div[@class="eslAddress1"]/text()'))
		item['address2'] = self.validate(detail.xpath('.//div[@class="eslAddress2"]/text()'))
		item['city'] = self.validate(detail.xpath('.//span[@class="eslCity"]/text()'))[:-1]
		item['state'] = self.validate(detail.xpath('.//span[@class="eslStateCode"]/text()'))
		item['zip_code'] = self.validate(detail.xpath('.//span[@class="eslPostalCode"]/text()'))
		item['country'] = 'United States'
		item['phone_number'] =self.validate(detail.xpath('.//div[@class="eslPhone"]/text()'))
		h_temp = ''
		hour_list = detail.xpath('.//span[@class="ml-storelocator-hours-details"]/text()').extract()
		for hour in hour_list:
			if hour.strip() != '':
				h_temp += hour.strip() + ' , '
		item['store_hours'] = h_temp[:-2]
		yield item

	def validate(self, item):
		try:
			item = item.extract_first()
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace('(','').replace(')','')
		except:
			return ''