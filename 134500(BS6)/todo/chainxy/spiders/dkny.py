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

class Dkny(scrapy.Spider):
	name = 'dkny'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://stores.dkny.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="location"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="location-name"]//span/text()'))
			item['address'] = self.validate(store.xpath('.//span[contains(@class,"c-address-street-1")]/text()'))
			item['address2'] = self.validate(store.xpath('.//span[contains(@class,"c-address-street-2")]/text()'))
			item['city'] = self.validate(store.xpath('.//span[contains(@class,"c-address-city")]//span/text()'))
			item['state'] = self.validate(store.xpath('.//abbr[contains(@class,"c-address-state")]/text()'))
			item['zip_code'] = self.validate(store.xpath('.//span[contains(@class,"c-address-postal-code")]/text()'))
			item['country'] = self.validate(store.xpath('.//abbr[contains(@class,"c-address-country-name")]/text()'))
			item['phone_number'] = self.validate(store.xpath('.//div[contains(@class,"location-phone")]//a/text()'))
			h_temp = ''
			week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			hour_list = store.xpath('.//div[contains(@class, "c-location-hours-today-details-row js-day-of-week-row")]')
			for hour in hour_list:
				h_temp += self.validate(week_list[int(self.validate(hour.xpath('./@data-day-of-week-end-index')))-1]) + ' ' 
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-today-day-hours-intervals-instance-open"]/text()')) + ' - '
				h_temp += self.validate(hour.xpath('.//span[@class="c-location-hours-today-day-hours-intervals-instance-close"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace(',','')
		except:
			return ''