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

class round(scrapy.Spider):
	name = 'round'
	domain = 'https://www.9round.com'
	history = ['']

	def start_requests(self):
		
		init_url  = 'https://www.9round.com/kickboxing-classes/US'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		print('---------------- checking ..................')
		state_list = response.xpath('//ul[@class="directions__list"]//li[@class="directions__item directions__item-region"]')
		for state in state_list : 
			url = self.validate(state.xpath('.//a/@href'))
			state_link = self.domain + url
			request = scrapy.Request(url=state_link, callback=self.parse_store)
			request.meta['state'] = self.validate(state.xpath('.//a/text()'))
			yield request
	
	def parse_store(self, response):
		store_list = response.xpath('//small//a[@class="directions__link"]')
		for store in store_list:
			url = self.validate(store.xpath('./@href'))
			detail_link = self.domain + url
			request = scrapy.Request(url=detail_link, callback=self.parse_detail)
			request.meta['state'] = response.meta['state']
			yield request

	def parse_detail(self, response):
		title = self.validate(response.xpath('//h1[@class="intro__slogan"]/text()'))
		item = ChainItem()
		if title == '':
			detail = response.xpath('//div[@class="media-left v-top club__info"]')
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(detail.xpath('.//span[@itemprop="streetAddress"]/text()'))
			item['city'] = self.validate(detail.xpath('.//span[@itemprop="addressLocality"]/text()'))
			item['state'] = self.validate(detail.xpath('.//span[@itemprop="addressRegion"]/text()'))
			item['zip_code'] = self.validate(detail.xpath('.//span[@itemprop="postalCode"]/text()'))
			item['country'] = self.validate(detail.xpath('.//span[@itemprop="addressCountry"]/text()'))
			item['phone_number'] = self.validate(detail.xpath('.//span[@itemprop="telephone"]//a/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = detail.xpath('.//table[@class="data-table club__hours"]//tr[@class="data-table__row"]')
			for hour in hour_list:
				for time in hour.xpath('.//td'):
					h_temp += self.validate(time.xpath('./text()')) + ' '
				h_temp += ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if item['phone_number'] not in self.history:
				self.history.append(item['phone_number'])
				yield item	
		else:
			item['city'] = self.validate(response.xpath('.//h1[@class="intro__slogan"]/text()')).split(',')[0].split(':')[1].strip()
			item['state'] = response.meta['state']
			item['coming_soon'] = '1'
			yield item
		
	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''