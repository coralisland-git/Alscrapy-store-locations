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
import pdb


class petpartnersusa(scrapy.Spider):
	name = 'petpartnersusa'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.petpartnersusa.com/our-practices/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//a[@class="et_pb_promo_button et_pb_button et_pb_custom_button_icon"]/@href').extract()
		print("=========  Checking.......", len(store_list))	
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//div[contains(@class, "et_pb_text_5")]//text()')
			for cnt in range(1, 10):
				detail = self.eliminate_space(response.xpath('//div[contains(@class, "et_pb_text_'+str(cnt)+'")]//text()').extract())
				if self.check_in('Phone', detail):
					item['store_name'] = self.validate(detail[1])
					address = detail[3]
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
					item['country'] = self.validate('United States')
					for cnt in range(1, len(detail)-1):
						if 'Phone' in detail[cnt-1] and ':' in detail[cnt]:
							item['phone_number'] = self.validate(detail[cnt].replace(':',''))
				if self.check_in('Hours of Operation', detail):
					h_temp = ''
					for cnt in range(1, len(detail)):
						h_temp += self.format(detail[cnt]) + ' '
					item['store_hours'] = self.validate(h_temp)
			yield item		

		except:
			pdb.set_trace()

	def check_in(self, item, arr):
		for a in arr:
			if item in a:
				return True
				break
		return False

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
			return item.encode('raw-unicode-escape').replace('\u2013', '').strip()
		except:
			return ''