from __future__ import unicode_literals
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
import time

class medicineshoppe(scrapy.Spider):
	name = 'medicineshoppe'
	domain = 'http://www.medicineshoppe.com'
	history = ['']

	def __init__(self, *args, **kwargs):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url  = 'http://www.medicineshoppe.com/pharmacy-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_location = []
		location_list =[]
		self.driver.get("http://www.medicineshoppe.com/pharmacy-locations")
		data = response.xpath('//ul[@class="state-search"]//li')
		for dat in data:
			if dat.xpath('./@class').extract_first() is None:
				location_list.append(dat.xpath('.//a/@id').extract_first())
				self.driver.find_element_by_id(dat.xpath('.//a/@id').extract_first()).click()
				time.sleep(5)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//div[@class="brand-content"]')
				for store in store_list:
					url_link = self.domain + store.xpath('.//h3[@class="brand-name"]//a/@href')[0].strip()
					yield scrapy.Request(url=url_link, callback=self.parse_page)
			
	def parse_page(self, response):
		try:
			store = response.xpath('//div[@class="inner-details"]')
			item = ChainItem()
			item['store_name'] = 'The Medicine Shoppe Pharmacy'
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//div[@class="scaddress"]/text()').extract_first())
			item['address2'] = ''
			address = self.validate(store.xpath('.//div[@class="sccityzip"]/text()').extract_first())
			item['city'] = address.split(',')[0].strip()
			item['state'] = address.split(',')[1].strip()[:2]
			item['zip_code'] = address.split(',')[1].strip()[2:].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//div[@class="contact-info"]//dd[1]/text()').extract_first())
			item['latitude'] = ''
			item['longitude'] = ''
			item['store_hours'] = ''
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="pharmacy-hours"]//text()').extract())
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
			if self.validate(item) != '' and 'hours' not in self.validate(item).lower() :
				tmp.append(self.validate(item))
		return tmp