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

class pigtailscrewcuts(scrapy.Spider):
	name = 'pigtailscrewcuts'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.pigtailsandcrewcuts.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[@id="content"]//li//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		with open('response.html', 'wb') as f:
			f.write(response.body)
		try:
			detail = response.xpath('//div[contains(@class, "wpb_column column_container col no-padding color-dark")][1]//div[contains(@class,"wpb_text_column wpb_content_element ")]')
			item = ChainItem()
			n_temp = self.eliminate_space(detail[0].xpath('.//strong//text()').extract())
			item['store_name'] = ''
			for temp in n_temp:
				item['store_name'] += temp.encode('raw-unicode-escape').replace('\u2013', '').strip() + ' '
			item['store_name'] = self.validate(item['store_name'])
			temp = self.eliminate_space(detail[1].xpath('.//table//tbody//text()').extract())
			address = ''
			h_temp = ''
			item['phone_number'] = ''
			for te in temp:
				if ':' in te:
					h_temp += te.encode('raw-unicode-escape').replace('\u2013', '-').strip() + ', '
				elif '-' in te : 
					item['phone_number'] = te
				else : 
					address += te + ', '
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
			if item['state'] != '':
				yield item
		except:
			pass	


	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\xa0', '').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'Memorial' not in self.validate(item) and 'Mothers' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp