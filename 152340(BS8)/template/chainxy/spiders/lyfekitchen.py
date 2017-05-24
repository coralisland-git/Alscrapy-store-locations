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

class lyfekitchen(scrapy.Spider):
	name = 'lyfekitchen'
	domain = 'http://www.lyfekitchen.com'
	history = []

	def start_requests(self):	
		init_url  = 'http://www.lyfekitchen.com'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		self.driver.get("http://www.lyfekitchen.com/?instant=1&s=#q=&page=0&refinements=%5B%5D&numerics_refinements=%7B%7D&index_name=%22lyfe_all%22")
		source = self.driver.page_source.encode("utf8")
		store_list = etree.HTML(source).xpath('//div[@class="result_details"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h1[@class="result-title"]//a/text()')[0])
			address_temp = self.eliminate_space(store.xpath('.//p[@class="lyfe_address"]//text()'))
			address = ''
			for temp in address_temp:
				address += temp + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			h_temp = ''
			hour_list = self.eliminate_space(store.xpath('.//p[@class="lyfe_hours"]//text()'))
			for hour in hour_list:
				if ':' in hour:
					h_temp += hour + ', '
				elif '-' in hour:
					item['phone_number'] = hour		
			item['store_hours'] = h_temp[:-2]
			yield item				
			
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''