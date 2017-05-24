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

class BS3Wabagrill(scrapy.Spider):
	name = 'BS3-Wabagrill'
	domain = 'https://www.wabagrill.com/'
	history = []

	def start_requests(self):
		url = 'http://www.wabagrill.com/index.php/Locations'
		yield scrapy.Request(url=url, callback=self.parse_store) 
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@class="mainbox"]//a[contains(@href, "http")]')	
		for store in store_list:
			store_link = self.validate(store.xpath('./@href'))
			yield scrapy.Request(url=store_link, callback=self.parse_detail)

	def parse_detail(self, response):
		print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',response.url)
		detail = response.xpath('//div[@class="blk_m"]')
		item = ChainItem()
		item['store_name'] = ''
		item['store_number'] = ''
		address = self.validate(detail.xpath('.//div[@class="line_2"][1]//div[@class="detail"]//a/text()')).split(',')
		if len(address) == 4:		
			item['address'] = address[0] 
			item['address2'] = address[1]
			item['city'] = address[2]
			item['state'] = address[3].split(' ')[0].strip()
			item['zip_code'] = address[3].split(' ')[1].strip()
		else:
			item['address'] = address[0] 
			item['address2'] = ''
			item['city'] = address[1]
			item['state'] = address[2].split(' ')[0].strip()
			item['zip_code'] = address[2].split(' ')[1].strip()			
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail.xpath('.//div[@class="line_2"][2]//div[@class="detail"]//a/text()'))
		geolocation = self.validate(detail.xpath('.//div[@class="line_2"][1]//div[@class="detail"]//a/@href')).split('/')
		geolocation = geolocation[len(geolocation)-1].split(',')
		item['latitude'] = geolocation[0]
		item['longitude'] = geolocation[1]
		item['store_hours'] = self.validate(detail.xpath('.//div[@class="line_2"][4]//div[@class="detail"]/text()'))
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item	

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('\n', '').replace('\r', '').replace(';','')
		except:
			return ''