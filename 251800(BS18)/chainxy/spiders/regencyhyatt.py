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
import pdb

class regencyhyatt(scrapy.Spider):
	name = 'regencyhyatt'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://regency.hyatt.com/content/brandredesign/en/hyattregency/locations/jcr:content/parsys/maps.hregencyjsonformat.html'
		header = {
			"accept":"application/json, text/javascript, */*; q=0.01",
			"accept-encoding":"gzip, deflate, br",
			"x-requested-with":"XMLHttpRequest"
		}
		yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = json.loads(response.body)['HOTELS']
		for con_name, continent in store_list:
			for cou_name, country in continent:
				for sto_name, store in country['NotAvailable']:
					item = ChainItem()
					item['store_name'] = self.validate(store['HOTEL_NAME'])
					# item['address'] = self.validate(store['address'])
					# item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['SPIRIT_CODE'])
					item['state'] = self.validate(store['HOTEL_STATE'])
					# item['zip_code'] = self.validate(store['zip'])
					item['country'] = self.validate(store['HOTEL_COUNTRY'])
					item['latitude'] = self.validate(store['LATITUDE'])
					item['longitude'] = self.validate(store['LONGITUDE'])
					link = self.validate(store['HOTEL_URL'])
					yield scrapy.Request(url=link, callback=self.parse_page)
				except:
					pdb.set_trace()		

	def parse_page(self, response):
		

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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

	def fixLazyJson (self, in_text):
		tokengen = tokenize.generate_tokens(StringIO(in_text).readline)
		result = []
		for tokid, tokval, _, _, _ in tokengen:
			if (tokid == token.NAME):
				if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
					tokid = token.STRING
					tokval = u'"%s"' % tokval
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
				if (len(result) > 0) and (result[-1][1] == ','):
					result.pop()			
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			result.append((tokid, tokval))

		return tokenize.untokenize(result)
