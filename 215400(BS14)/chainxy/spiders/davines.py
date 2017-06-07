# from __future__ import unicode_literals
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
import tokenize
import token
from StringIO import StringIO

class davines(scrapy.Spider):
	name = 'davines'
	domain = 'http://www.davines.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_Cities_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_Cities_list = json.load(data_file)

	def start_requests(self):
		# for location in self.US_Cities_list:
		# 	init_url = 'http://www.davines.com/en/salon-locator/?country=US&citypostal=%s&specialty=all' %location['city']
		# 	yield scrapy.Request(url=init_url, callback=self.body) 
		for location in self.CA_Cities_list:
			init_url = 'http://www.davines.com/en/salon-locator/?country=CA&citypostal=%s&specialty=all' %location['city'].split('(')[0].strip()
			yield scrapy.Request(url=init_url, callback=self.body)

	def body(self, response):
		data = response.body.split('var locations = [];')[1].split('$(document).ready(function() {')[0].strip()
		store_list = data.split('locations.push(')
		for store in store_list[1:]:
			try:
				store = json.loads(self.fixLazyJson(self.format(store.strip()[:-2])))
				item = ChainItem()
				item['store_name'] = self.validate(store['title'])
				address = self.validate(store['address'])
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
				item['country'] = self.validate(store['country'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pdb.set_trace()		

		pagenation = response.xpath('//a[@class="pagination-next"]/@href').extract_first()
		if pagenation:
			pagenation = self.domain + pagenation
			yield scrapy.Request(url=pagenation, callback=self.body)

	def validate(self, item):
		try:
			return item.strip().replace('<br>',',').replace(';','')
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
			return item.decode('UTF-8').strip()
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
