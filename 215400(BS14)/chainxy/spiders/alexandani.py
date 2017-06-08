from __future__ import unicode_literals
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

class alexandani(scrapy.Spider):
	name = 'alexandani'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.alexandani.com/locations/country/'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		formdata = {
			"country":"US"
		}
		yield scrapy.FormRequest(url=init_url, formdata=formdata, headers=header, method='post', callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//table[@class="aa-locations"]/tr/td')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item['phone_number'] = ''
				item['store_name'] = detail[0]
				address = ''
				for de in detail[1:]:
					if '(' in de or '@' in de or 'direction' in de: 
						break
					address += de + ', '	
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address[:-2])
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = 'United States'
				h_temp = ''
				count = 0
				for ind in range(0, len(detail)):
					if '(' in detail[ind] and '-' in detail[ind]: 
						item['phone_number'] = detail[ind]
				yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\r','').replace('\n','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp