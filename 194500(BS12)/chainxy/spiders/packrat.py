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

class packrat(scrapy.Spider):
	name = 'packrat'
	domain = 'https://www.1800packrat.com'
	history = []

	def start_requests(self):
		init_url = 'https://www.1800packrat.com/locations'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch, br",
			
		}
		yield scrapy.Request(url=init_url,  callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//a[@class="location-list__city"]/@href').extract()
		for store in store_list:
			store = self.domain + store
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"Referer":"https://www.1800packrat.com/locations/"
			}
			yield scrapy.Request(url=store, headers=header, method='get',callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[@class="location-overlay"]//text()').extract())
			address = ''
			item['phone_number'] = ''
			for de in detail:
				if ':' not in de and '-' in de:
					item['phone_number'] = de
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
			for de in detail:
				if ':' in de:
					h_temp += de + ', '
			item['store_hours'] = h_temp[:-2]
			yield item	
		except:
			pdb.set_trace()

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