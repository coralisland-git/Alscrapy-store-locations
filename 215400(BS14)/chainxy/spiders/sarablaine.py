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

class sarablaine(scrapy.Spider):
	name = 'sarablaine'
	domain = 'http://sarablaine.com/locate-retailer.php'
	history = []


	def start_requests(self):
		init_url = 'http://sarablaine.com/locate-retailer.php'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		print("=========  Checking.......")
		data = "<div>"+response.body.split('alternateContent =')[1].split('document.write')[0].strip().replace('+','').replace("'",'')+"</div>"
		tree = etree.HTML(data)
		state_list = tree.xpath('//map[@name="Map"]//area/@href')
		for state in state_list:
			try:
				if state != '#':
					state = self.domain + state
					header = {
						"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
						"Accept-Encoding":"gzip, deflate, sdch"
					}
					yield scrapy.Request(url=state, headers=header, callback=self.parse_city)
			except:
				pass

	def parse_city(self, response):
		city_list = response.xpath('//ul[@id="sddm"]//a/@href').extract()
		for city in city_list:
			city = self.domain + city.strip()
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, sdch"
			}
			yield scrapy.Request(url=city, callback=self.parse_page)

	def parse_page(self, response):
		detail = self.eliminate_space(response.xpath('//div[@id="city_locations"]/div[2]//text()').extract())
		try:
			item = ChainItem()
			item['store_name'] = detail[0]
			address = ''
			for de in detail[1:]:
				address += de + ', '
			item['city'] = ''
			addr_list = self.eliminate_space(address.split(','))
			item['address'] = addr_list[0]
			item['city'] = addr_list[-2]
			item['state'] = response.url.split('st=')[1].split('&')[0].strip().upper()
			item['zip_code'] = addr_list[-1]
			item['country'] = 'United States'
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