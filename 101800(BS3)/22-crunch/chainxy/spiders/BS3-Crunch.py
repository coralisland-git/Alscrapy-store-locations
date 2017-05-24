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

class BS3Crunch(scrapy.Spider):
	name = 'BS3-Crunch'
	domain = 'https://www.crunch.com'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):

		init_url  = 'https://www.crunch.com/locations'
		yield scrapy.Request(url=init_url, callback=self.parse_store) 
	
	def parse_store(self, response):
		store_location = []
		location_list =[]
		self.driver.get("https://www.crunch.com/locations")
		time.sleep(1)
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		store_list = tree.xpath('//div[@class="locations-grid"]//a/@href')
		for store in store_list:
			store_link = self.domain + store
			yield scrapy.Request(url=store_link, callback=self.parse_detail)

	def parse_detail(self, response):
		detail = response.xpath('//div[@class="hero__content type--center"]')
		item = ChainItem()
		item['store_name'] = self.validate(detail.xpath('.//h1/text()'))
		item['store_number'] = ''
		address = self.validate(detail.xpath('.//div[@class="hero__content__info"]/p[1]/text()')).split(',')
		if len(address) == 4:		
			item['address'] = address[0] 
			item['address2'] = address[1]
			item['city'] = address[2]
			item['state'] = address[3].strip().split(' ')[0].strip()
			item['zip_code'] = address[3].strip().split(' ')[1].strip()
		else:
			item['address'] = address[0] 
			item['address2'] = ''
			item['city'] = address[1]
			item['state'] = address[2].strip().split(' ')[0].strip()
			item['zip_code'] = address[2].strip().split(' ')[1].strip()			
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail.xpath('.//div[@class="hero__content__info"]//p[2]/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		check_list = response.xpath('//div[@class="tab-module__content__group"]')
		for check in check_list:
			if self.validate(check.xpath('./h2/text()')) == 'Hours of Fun':
				hour_list = check.xpath('.//ul//li//p[@class="list-block__item__link__title type--c5 type--gray-light"]//span/text()').extract()
				for hour in hour_list:
					h_temp += hour.strip() + ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		if item['store_name']+str(item['phone_number']) not in self.history:
			yield item
			self.history.append(item['store_name']+str(item['phone_number']))
	

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('\n', '').replace('\r', '').replace(';','')
		except:
			return ''