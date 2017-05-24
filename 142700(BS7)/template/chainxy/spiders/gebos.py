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


class gebos(scrapy.Spider):
	name = 'gebos'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.gebos.com/locations.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = response.xpath('//div[@class="location_entry"]')
			for store in store_list:
				detail = self.eliminate_space(store.xpath('.//text()').extract())
				item = ChainItem()
				item['store_name'] = self.validate(detail[0])
				item['city'] = ''
				item['address'] = ''
	 			address = detail[1] + ', ' + detail[2]
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0]
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = 'United States'
				item['phone_number'] = self.validate(detail[6])
				item['store_hours'] = self.validate(detail[11]) + ' '+ self.validate(detail[12]) + ', '
				item['store_hours'] += self.validate(detail[13]) + ' ' + self.validate(detail[14])
				yield item		
		except:
			pass

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