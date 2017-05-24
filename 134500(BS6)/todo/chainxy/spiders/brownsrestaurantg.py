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

class brownsrestaurantg(scrapy.Spider):
	name = 'brownsrestaurantg'
	domain = 'http://brownssocialhouse.com'
	history = []

	def start_requests(self):
		init_url = 'http://brownssocialhouse.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//nav[@id="mainNavigation"]//div[@class="folder"][2]//div[@class="collection"]//a/@href').extract()
		for state in state_list:
			state_url = self.domain + state
			yield scrapy.Request(url=state_url, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="sqs-block-content"]//a')
		for store in store_list:
			store = self.validate(store.xpath('./@href').extract_first())
			if self.domain in store:
				yield scrapy.Request(url=store, callback=self.parse_page)
	
	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="page-title"]/text()').extract_first())
			detail = response.xpath('//div[@class="page-description"]//text()').extract()
			addr = self.validate(detail[0]).split(',')
			addr_detail = []
			if len(addr) == 3:
				item['address'] = addr[0].strip()
				item['city'] = addr[1].strip()
				addr_detail = addr[2].strip().split(' ')
			elif len(addr)  == 2:
				c_addr = addr[0].split(' ')
				a_temp = ''
				item['city'] = c_addr[len(c_addr)-1]
				for ca in c_addr:
					a_temp += ca +' '
				item['address'] = a_temp.strip()	
				addr_detail = addr[1].strip().split(' ')
			elif len(addr) == 4:
				item['address']= addr[0].strip() + addr[1].strip()
				item['city'] = addr[1].strip()
				addr_detail = addr[3].strip().split(' ')
				addr_detail.append(addr[2].strip())

			elif len(addr) == 5:
				item['address'] = addr[0].strip() + addr[1].strip()
				item['city'] = addr[2].strip()
				addr_detail.append(addr[3].strip())
				addr_detail.append(addr[4].strip().split(' ')[0].strip())
				addr_detail.append(addr[4].strip().split(' ')[1].strip())

			z_temp = ''
			s_temp = ''
			for ad in addr_detail:
				if len(ad) == 3:
					z_temp += ad + ' '
				else :
					s_temp += ad + ' '
			item['state'] = s_temp.strip()
			item['zip_code'] = z_temp.strip()
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(detail[1])
			h_temp = ''
			hour_list = response.xpath('//div[contains(@class, "sqs-block-html")][2]//p/text()').extract()
			for hour in hour_list:
				h_temp += self.validate(hour) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''