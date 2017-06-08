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
import geocoder
import usaddress

class michaelkors(scrapy.Spider):
	name = 'michaelkors'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.michaelkors.com/server/countries'
		header = {
			"Accept":"application/json, text/plain, */*",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		country_list = json.loads(response.body)['countries']
		for country in country_list:
			state_list = country['states']
			country_name = country['name']
			for state in state_list:
				city_list = state['cities']
				for city in city_list:
					try:
						url = 'https://www.michaelkors.com/server/stores'
						header = {
							"Accept":"application/json, text/plain, */*",
							"Accept-Encoding":"gzip, deflate, br",
							"Content-Type":"application/json;charset=UTF-8"
						}
						g = geocoder.google(city['name'])
						payload = {
							"country":country_name,
							"latitude":str(g.latlng[0]),
							"longitude":str(g.latlng[1]),
							"radius":"300"
						}
						yield scrapy.Request(url=url, headers=header, body=json.dumps(payload), method='post', callback=self.parse_page)
					except:
						pass

	def parse_page(self, response):
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['displayName'])
				try:
					item['store_number'] = self.validate(store['locationId'])
				except:
					pass
				item['address'] = ''
				try:
					item['address'] = self.validate(store['address']['addressLine1'])
				except:
					pass
				try:
					item['address2'] = self.validate(store['address']['addressLine2'])
				except:
					pass
				try:
					item['city'] = self.validate(store['address']['city']['name'])
				except:
					pass
				try:
					item['state'] = self.validate(store['address']['state']['name'])
				except:
					pass
				try:
					item['zip_code'] = self.validate(store['address']['zipcode'])
				except:
					pass
				item['country'] = self.validate(store['address']['country']['name'])
				item['phone_number'] = ''
				try:
					item['phone_number'] = self.validate(store['address']['phone'])
				except:
					pass
				try:
					item['latitude'] = self.validate(store['geoLocation']['latitude'])
					item['longitude'] = self.validate(store['geoLocation']['longitude'])
				except:
					pass
				try:
					item['store_hours'] = self.validate(store['operatingHours'])
				except:
					pass
				try:
					item['store_type'] = self.validate(store['type'])
				except:
					pass
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''
