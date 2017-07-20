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

class countrymax(scrapy.Spider):
	name = 'countrymax'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.countrymax.com/Store-Locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('.//div[@class="dialog"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		if 'Virtual' not in response.url:
			try:
				detail = self.eliminate_space(response.xpath('//table//td[1]//text()').extract())	
				item = ChainItem()
				item['address'] = ''
				item['city'] = ''
				a_temp = ''
				for cnt in range(1, len(detail)):
					if detail[cnt].strip()[-1:] == ',':
						detail[cnt] = detail[cnt][:-1]
					a_temp += detail[cnt] + ' '
					if ',' in detail[cnt]:
						break
				addr = usaddress.parse(self.validate(a_temp))
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
				h_temp = ''
				for cnt in range(0,len(detail)-1):
					if 'Phone:' in detail[cnt] and '-' in detail[cnt+1]:
						item['phone_number'] = self.validate(detail[cnt+1])
						for ind in range(cnt+3, len(detail) -2):
							h_temp += detail[ind] + ', '
					if 'Phone:' in detail[cnt] and '-' in detail[cnt]:
						item['phone_number'] = self.validate(detail[cnt].split('Phone:')[1])
						for ind in range(cnt+2, len(detail) -3):
							h_temp += detail[ind] + ', '

				item['store_hours'] = h_temp[:-2]
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