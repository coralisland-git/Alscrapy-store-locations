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

class landmarkindustries(scrapy.Spider):
	name = 'landmarkindustries'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.landmarkindustries.com/retail.htm'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		
		detail = self.eliminate_space(response.xpath('//table[@width="530"]//td//p//text()').extract())
		temp = ''
		for cnt in range(0, len(detail)/4):
			cnt *= 4
			item = ChainItem()
			item['store_name'] = self.validate(detail[cnt])
			address = detail[cnt+1] + ', ' + detail[cnt+2]
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
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
			item['phone_number'] = self.validate(detail[cnt+3])
			yield item		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != 'Car Wash On-Site!':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''