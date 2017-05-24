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

class musclemakergr(scrapy.Spider):
	name = 'musclemakergr'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://musclemakergrill.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@class, "col-md-12 item")]')
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			try:
				item = ChainItem()
				item['latitude'] = self.validate(str(store.xpath('./@data-lat').extract_first()))
				item['longitude'] = self.validate(str(store.xpath('./@data-lng').extract_first()))
				item['coming_soon'] = '0'
				store = store.xpath('.//text()').extract()
				tmp = []
				for st in store:
					if self.validate(st) != '':
						if 'COMING SOON!' in self.validate(st) :
							item['coming_soon'] = '1'
						else:
							tmp.append(self.validate(st) )
				store = tmp
				item['store_name'] = store[0] + ' ' + store[1]
				item['address'] = store[2]
				addr = store[3].split(',')
				item['city'] = addr[0].strip()
				item['state'] = addr[1].strip().split(' ')[0].strip()
				item['zip_code'] = addr[1].strip().split(' ')[1].strip()
				item['country'] = 'United States'
				h_temp = ''
				p_temp = ''
				item['phone_number'] = ''
				for hour in store :
					if '-' in hour.lower():
						if '(' in hour and len(hour) < 16:
							p_temp += hour + ', '
						if 'am' in hour:
							h_temp += hour + ', '
				item['store_hours'] = h_temp[:-2]
				item['phone_number'] = p_temp[:-2]
				yield item
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace('\n','').replace('\r', '')
		except:
			return ''