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

class brownsshoes(scrapy.Spider):
	name = 'brownsshoes'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.brownsshoes.com/2014-store-locator-custom/2014-store-locator-custom,default,pg.html'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table')
		for cnt in range(0, len(store_list)/2):
			try:
				cnt *= 2
				item = ChainItem()
				detail = self.eliminatespace(store_list[cnt].xpath('.//text()').extract())
				hour_list_name = self.eliminatespace(store_list[cnt+1].xpath('.//tr[2]//td[1]//text()').extract())
				hour_list_time = self.eliminatespace(store_list[cnt+1].xpath('.//tr[2]//td[2]//text()').extract())
				item['store_name'] = self.validate(detail[0])
				if len(detail) == 5:
					item['address'] = self.validate(detail[1])		
					csz = detail[2].split(',')		
					item['city'] = self.validate(csz[0])
					if len(csz) ==4 :
						item['state'] = self.validate(csz[1])
						item['zip_code'] = self.validate(csz[2])
					else:
						addr = self.eliminatespace(csz[1].strip().split(' '))
						item['state'] = self.validate(addr[0])
						item['zip_code'] = self.validate(addr[1]) + ' ' + self.validate(addr[2])
					item['phone_number'] = self.validate(detail[3])
				else:
					csz = detail[1].split(',')
					item['address'] = self.validate(csz[0])
					item['city'] = self.validate(csz[1])
					if len(csz) == 4:
						item['state'] = self.validate(csz[2])
						item['zip_code'] = self.validate(csz[3])
					else:
						addr = self.eliminatespace(csz[2].strip().split(' '))
						item['state'] = self.validate(addr[0])
						item['zip_code'] = self.validate(addr[1]) + ' ' + self.validate(addr[2])
					item['phone_number'] = self.validate(detail[2])
				item['country'] = 'Canada'
				h_temp = ''
				for cnt in range(0, len(hour_list_time)-1):
					h_temp += self.validate(hour_list_name[cnt]) + ' ' + self.validate(hour_list_time[cnt]) + ', '
				item['store_hours'] = h_temp[:-2]
				yield item			
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

	def eliminatespace(self, items):
		tmp = []
		for item in items:
			if item.strip() != '':
				tmp.append(item.strip())
		return tmp