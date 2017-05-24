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

class BS3Titleboxingclub(scrapy.Spider):
	name = 'BS3-Titleboxingclub'
	domain = 'https://titleboxingclub.com/locations/states/'
	history = []

	def start_requests(self):
		url = 'https://titleboxingclub.com/locations/states/?'
		yield scrapy.Request(url=url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="padding find-header"]//ul/li')		
		for state in state_list : 
			go_url = self.validate(state.xpath('.//a/@href'))
			state_link = self.domain + go_url
			yield scrapy.Request(url=state_link, callback=self.parse_store)
	
	def parse_store(self, response):
		store_list = response.xpath('//div[@id="map-list"]//div[@class="store"]//a[contains(@href, "https")]')
		for store in store_list:
			store_link = self.validate(store.xpath('./@href'))
			yield scrapy.Request(url=store_link, callback=self.parse_detail)

	def parse_detail(self, response):
		with open('page.html','wb') as f:
			f.write(response.body)
		detail = response.xpath('//div[@class="location-header"]')
		item = ChainItem()
		item['store_name'] = self.validate(detail.xpath('.//h2[@class="h-lg"]/text()'))
		item['store_number'] = ''
		item['address'] = self.validate(detail.xpath('.//p[@class="desktop"]//span[@class="address1"]/text()'))
		item['address2'] = ''
		address = self.validate(detail.xpath('.//p[@class="desktop"]//span[@class="address2"]/text()'))		
		item['city'] = address.split(',')[0].strip()
		temp = address.split(',')[1].strip().split(' ')
		state = ''
		for cnt in range(0,len(temp)-1):
			state += temp[cnt] + ' '
		item['state'] = state.strip()
		item['zip_code'] = temp[len(temp)-1]
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail.xpath('.//p[@class="desktop"]//span[@class="phone"]/text()'))
		item['latitude'] = ''
		item['longitude'] = ''
		h_temp = ''
		hour_list = detail.xpath('.//p[@class="desktop"]//span[@class="hours"]/span')
		for hour in hour_list : 
			h_temp += self.validate(hour.xpath('./span/text()')) + ' ' + self.validate(hour.xpath('./text()')) + ', '
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