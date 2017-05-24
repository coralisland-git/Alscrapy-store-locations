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

class BS3Gndermountain(scrapy.Spider):
	name = 'BS3-Gandermountain'
	domain = 'http://www.gandermountain.com'
	history = []

	def start_requests(self):
	
		init_url  = 'http://www.gandermountain.com/store-locator/list/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//table[@id="store_page"]//a[@class="body"]/@href').extract()
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//div[@class="storepage_location"]//p')
		item = ChainItem()
		item['store_name'] = ''
		item['store_number'] = self.validate(detail[0].xpath('.//b/text()')).split('#')[1][:-1]
		item['address'] = self.validate(detail[1].xpath('./text()'))
		item['address2'] = ''
		address = self.validate(detail[2].xpath('./text()')).split(',')
		item['city'] = address[0]
		item['state'] = address[1].split(' ')[0].strip()
		item['zip_code'] = address[1].split(' ')[1].strip()	
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail[3].xpath('./text()'))
		item['latitude'] = self.validate(detail[6].xpath('./text()')).split(':')[1].strip()
		item['longitude'] = self.validate(detail[7].xpath('./text()')).split(':')[1].strip()
		h_temp = ''
		hour_list = response.xpath('.//div[@class="storepage_location"]//table//tr')
		for hour in hour_list:
			time_list = hour.xpath('.//td/text()').extract()
			for time in time_list:
				h_temp += time.strip() + ' '
			h_temp += ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('\n', '').replace('\r', '').replace(';','')
		except:
			return ''