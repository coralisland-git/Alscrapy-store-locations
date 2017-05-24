import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
import geocoder

from selenium import webdriver
from lxml import html
import geocoder
import pdb

class orangetheoryfitness(scrapy.Spider):
	name = 'orangetheoryfitness'
	domain = 'https://www.orangetheoryfitness.com/'
	history = ['']

	def __init__(self):
		self.country_list = ['Australia','Canada','Colombia','Dominican Republic','Mexico','Peru','United Kingdom','United States']

	def start_requests(self):
		init_url = 'https://www.orangetheoryfitness.com/locations-list'
		yield scrapy.Request(url=init_url, callback=self.parse_store_list)
		

	def parse_store_list(self, response):
		print('=============================')
		data_list = response.xpath('//div[contains(@class,"list-inner country-container")]')		
		for data in data_list:
			if data.xpath('./@data-country-name').extract_first() in self.country_list:
				store_list = data.xpath('.//li')
				for store in store_list:
					try:
						detail_url = store.xpath('.//a/@href').extract_first()
						request = scrapy.Request(url=detail_url, callback=self.parse_detail)
						request.meta['country'] = data.xpath('./@data-country-name').extract_first()
						yield request
					except:
						pass

	def parse_detail(self, response):
		print("=========  Checking.......")
		detail = response.xpath('.//div[@class="mobilePad"]')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('.//div[@class="otfLocationTitle"]//p/text()').extract_first())
			item['store_number'] = ''
			address = self.eliminate_space(detail.xpath('.//div[@class="otfAddress"]//text()').extract())
			item['address'] = self.validate(address[0])
			item['address2'] = ''
			item['city'] = self.validate(address[1].split(',')[0].strip())
			item['state'] = self.validate(address[1].split(',')[1].strip())
			item['zip_code'] = self.validate(address[1].split(',')[2].strip())
			item['country'] = response.meta['country']
			item['phone_number'] = self.validate(detail.xpath('.//div[@class="otfInfoLinks"]//a[1]/text()').extract_first())
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