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

class zumiez(scrapy.Spider):
	name = 'zumiez'
	domain = 'http://www.zumiez.com/'
	history = ['']

	def start_requests(self):
		init_url  = 'http://www.zumiez.com/storelocator/list/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//ul[@class="accordion-content"]/li')
		for store in store_list:
			link_url = store.xpath('.//strong//a/@href').extract_first()
			yield scrapy.Request(url=link_url, callback=self.parse)

	def parse(self, response):
		data = response.xpath('//div[@class="store-page"]')
		item = ChainItem()
		item['store_name'] = self.eliminater(self.validate(data.xpath('.//h3[@class="uppercase"]/text()')))
		item['store_number'] = response.url.split('/')[7]
		item['address'] = self.eliminater(self.validate(data.xpath('.//address//span[@itemprop="streetAddress"]/text()')))
		item['address2'] = ''
		item['city'] = self.validate(data.xpath('.//address//span[@itemprop="addressLocality"]/text()'))[:-1]
		item['state'] = self.validate(data.xpath('.//address//span[@itemprop="addressRegion"]/text()'))
		item['zip_code'] = self.validate(data.xpath('.//address//span[@itemprop="postalCode"]/text()'))
		item['country'] = 'United States'
		item['phone_number'] = self.validate(data.xpath('.//div[@itemprop="telephone"]//a/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		try:
			h_temp = ''
			hour_list = data.xpath('.//section//time[@itemprop="openingHours"]')
			for hour in hour_list : 
				h_temp = h_temp + self.validate(hour.xpath('.//span[1]/text()')) + self.validate(hour.xpath('.//span[2]/text()'))
				hhh = hour.xpath('.//span[3]/text()').extract() 
				h_temp = h_temp + ' : ' + hhh[0].strip() + hhh[2].strip() + ', '
			item['store_hours'] = h_temp[:-2]
		except:
			item['store_hours'] = ''			
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		if item['store_name']+str(item['store_number']) not in self.history:
			yield item
			self.history.append(item['store_name']+str(item['store_number']))
	
	def eliminater(self, item):
		return item.replace('&amp;', ' ').replace(';', ',').replace(',;', ',')

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''			