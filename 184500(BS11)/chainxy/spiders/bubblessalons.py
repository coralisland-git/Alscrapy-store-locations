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

class bubblessalons(scrapy.Spider):
	name = 'bubblessalons'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.bubblessalons.com/api/content/render/false/type/xml/query/+structureName:BubblesSalonLocations%20+(conhost:48190c8c-42c4-46af-8d1a-0cd5db894797%20conhost:SYSTEM_HOST)%20+languageId:1*%20+deleted:false%20+live:true%20%20+working:true/orderby/modDate%20desc/limit/50'
		header = {
			"Accept":"application/xml, text/xml, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, sdch",
			"X-Requested-With":"XMLHttpRequest"
			}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//content')
		store_number_list = response.body.split('<salonNo>')
		zipcode_list = response.body.split('<zipCode>')
		store_hours_list = response.body.split('<storeHours>')
		for cnt in range(0, len(store_list)):
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store_list[cnt].xpath('.//title/text()').extract_first())
				item['store_number'] = self.validate(store_number_list[cnt+1].split('</salonNo>')[0])
				item['address'] = self.validate(store_list[cnt].xpath('.//address/text()').extract_first())
				item['city'] = self.validate(store_list[cnt].xpath('.//city/text()').extract_first())
				item['state'] = self.validate(store_list[cnt].xpath('.//state/text()').extract_first())
				item['zip_code'] = self.validate(zipcode_list[cnt+1].split('</zipCode>')[0])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store_list[cnt].xpath('.//phone/text()').extract_first())
				item['latitude'] = self.validate(store_list[cnt].xpath('.//latitude/text()').extract_first())
				item['longitude'] = self.validate(store_list[cnt].xpath('.//longitude/text()').extract_first())
				item['store_hours'] = self.validate(store_hours_list[cnt+1].split('</storeHours>')[0])[1:-1].replace('=', ' ')
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