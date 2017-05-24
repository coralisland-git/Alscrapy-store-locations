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

class kirklands(scrapy.Spider):
	name = 'kirklands'
	domain = 'https://www.kirklands.com'

	def start_requests(self):
		init_url  = 'http://www.kirklands.com/custserv/locate_store.cmd'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="colGroup"]//div[@class="col33 store"]')
		for store in store_list:
			link = store.xpath('.//div[@class="inner"]//a[@class="saveStore"]/@href').extract_first()
			link = self.domain + link
			yield scrapy.Request(url=link, callback=self.parse_page)

	def parse_page(self, response):
		store = response.xpath('//div[@id="storeLocator"]')
		item = ChainItem()
		item['store_name'] = self.validate(store.xpath('.//h1/text()'))
		item['store_number'] = ''
		address = store.xpath('.//div[@class="colGroup storeInfo"]//div[@itemprop="address"]')
		item['address'] = self.validate(address.xpath('.//span[@itemprop="streetAddress"]/text()'))
		if len(address.xpath('.//span[@itemprop="addressLocality"]')) == 2:
			item['address2'] = self.validate(address.xpath('.//span[@itemprop="addressLocality"][1]/text()'))
			item['city'] = self.validate(address.xpath('.//span[@itemprop="addressLocality"][2]/text()'))
		else : 
			item['address2'] = ''
			item['city'] = self.validate(address.xpath('.//span[@itemprop="addressLocality"][1]/text()'))
		item['state'] = self.validate(address.xpath('.//span[@itemprop="addressRegion"]/text()'))
		item['zip_code'] = self.validate(address.xpath('.//span[@itemprop="postalCode"]/text()'))
		item['country'] = 'United States'
		item['phone_number'] = self.validate(address.xpath('.//span[@itemprop="telephone"]/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = store.xpath('.//div[@class="hours"]//time//span')
		for hour in hour_list:
			h_temp += self.validate(hour.xpath('.//meta[@itemprop="dayOfWeek"]/@content')) + ' : ' + self.validate(hour.xpath('.//meta[@itemprop="opens"]/@content')) + ' - ' + self.validate(hour.xpath('.//meta[@itemprop="closes"]/@content')) +', '
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