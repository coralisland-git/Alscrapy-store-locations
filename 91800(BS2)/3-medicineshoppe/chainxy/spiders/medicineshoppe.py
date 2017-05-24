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

	def __init__(self):
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
		print('---------------parse_page--------------')
		store = response.xpath('//div[@class="inner-details"]')
		item = ChainItem()
		item['store_name'] = 'The Medicine Shoppe Pharmacy'
		item['store_number'] = ''
		item['address'] = self.validate(store.xpath('.//div[@class="scaddress"]/text()'))
		item['address2'] = ''
		address = self.validate(store.xpath('.//div[@class="sccityzip"]/text()'))
		print('!!!!!!!!!!!!!!!!!!!!', address)
		item['city'] = address.split(',')[0].strip()
		item['state'] = address.split(',')[1].strip()[:2]
		item['zip_code'] = address.split(',')[1].strip()[2:].strip()
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//div[@class="contact-info"]//dd[1]/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		item['store_hours'] = ''
		h_temp = ''
		week_list = response.xpath('//div[@class="pharmacy-hours"]//strong/text()').extract()
		if len(week_list) == 0:
			hour_list = response.xpath('//div[@class="pharmacy-hours"]//ul//li')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//div[@class="day"]/text()')) + self.validate(hour.xpath('.//div[@class="time"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
		else:			
			hour_list = response.xpath('//div[@class="pharmacy-hours"]/text()').extract()
			for cnt in range(0,len(week_list)-1):
				h_temp += week_list[cnt].strip() + hour_list[2*cnt+1].strip() + ', ' 
			item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item


	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''