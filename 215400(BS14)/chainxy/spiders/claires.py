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

class claires(scrapy.Spider):
	name = 'claires'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.claires.com/us/pws/StoreFinder.ice?'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		country_list = response.xpath('//select[@id="country"]//option')
		for country in country_list:
			country_name = country.xpath('./text()').extract_first()
			country_abbr = country.xpath('./@value').extract_first()
			if country_abbr != '':
				url = 'http://www.claires.com/us/pws/StoreFinder.ice?findCountryRegions=true&country=%s&ajax=true' %country_abbr
				self.header = {
					"Accept":"application/json, text/javascript, */*; q=0.01",
					"Accept-Encoding":"gzip, deflate, sdch",
					"X-Requested-With":"XMLHttpRequest"
				}
				yield scrapy.Request(url=url, headers=self.header, callback=self.parse_state, meta={'country_abbr':country_abbr, 'country_name':country_name})

	def parse_state(self, response):
		try:
			state_list = json.loads(response.body)['countryRegions']
			if len(state_list) < 3:
				url = 'http://www.claires.com/us/pws/StoreFinder.ice?findStore=true&country=%s&ajax=true' %response.meta['country_abbr']
				yield scrapy.Request(url=url, headers=self.header, callback=self.parse_page, meta={'country_name':response.meta['country_name']})
			else:
				for state in state_list:
					if state != '':
						url = 'http://www.claires.com/us/pws/StoreFinder.ice?findStore=true&country=%s&countryRegion=%s&ajax=true' %(response.meta['country_abbr'], state)
						yield scrapy.Request(url=url, headers=self.header, callback=self.parse_page, meta={'country_name':response.meta['country_name']})
		except:
			pass

	def parse_page(self, response):
		try:
			store_list = json.loads(response.body)['stores']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['name'])
					item['store_number'] = self.validate(str(store['id']))
					item['address'] = self.validate(store['address1'])
					item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['postcode'])
					item['country'] = response.meta['country_name']
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					h_temp = ''
					week_list = ['mon','tue', 'wed', 'thu', 'fri', 'sat', 'sun']
					for week in week_list:
						try:
							if self.validate(store[week+'OpenTimes']) != '':
								h_temp += week.upper() + ' ' + self.validate(store[week+'OpenTimes']) + ', '
						except:
							pass
					item['store_hours'] = h_temp[:-2]
					yield item	
				except:
					pass
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp