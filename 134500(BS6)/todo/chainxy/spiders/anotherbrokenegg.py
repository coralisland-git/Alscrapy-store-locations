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

class Anotherbrokenegg(scrapy.Spider):
	name = 'anotherbrokenegg'
	domain = 'http://anotherbrokenegg.com'
	history = []
	cnt = 0

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://anotherbrokenegg.com/list-indexed-business?'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		next_url = self.validate(response.xpath('//a[@title="Go to next page"]/@href').extract_first())

		store_list = response.xpath('.//div[contains(@class, "view-content")]//div[contains(@class,"views-row")]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="field-tile"]//a/text()').extract_first())
			detail = store.xpath('.//div[contains(@class,"field-address")]//text()').extract()
			temp = []
			for de in detail:
				if self.validate(de) != '':
					temp.append(self.validate(de))
			item['address'] = temp[0]
			addr = temp[1].split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[contains(@class,"field-phone")]//a/text()').extract_first())
			h_temp = ''
			hour_list = store.xpath('.//div[@class="field-open-time"]//text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '' and 'am' in self.validate(hour).lower():
					h_temp += self.validate(hour) +', '
			item['store_hours'] = h_temp[:-2]
			yield item			

		if next_url is not None:
			next_url = self.domain + next_url
			yield scrapy.Request(url=next_url,callback=self.body)
		
		
	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''