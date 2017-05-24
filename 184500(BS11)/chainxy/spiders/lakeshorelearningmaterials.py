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

class lakeshorelearningmaterials(scrapy.Spider):
	name = 'lakeshorelearningmaterials'
	domain = 'http://www.lakeshorelearning.com/general_content/store_locations/'
	history = []

	def start_requests(self):
		init_url = 'http://www.lakeshorelearning.com/general_content/store_locations/storeLocations.jsp'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//tr[@class="store_locations_view_all"]//a/@href').extract()
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="mainContent"]//table//tr[3]//td//text()').extract())
			address = ''
			h_temp = ''
			limit = 0
			for cnt in range(0, len(detail)):
				if 'sunday' in detail[cnt].lower():
					limit = cnt
					break 
			for de in detail[:limit+1]:
				if ':' in de or 'closed' in de.lower():
					h_temp += de + ', '
				elif '-' in de:
					if 'fax' not in de.lower():
						item['phone_number'] = de
				else :
					address += de + ', '
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
