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
import tokenize
import token
from StringIO import StringIO


class icuracao(scrapy.Spider):
	name = 'icuracao'
	domain = 'http://icuracao.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://icuracao.com/store-locator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = self.format(response.body).split('var storeList = ')[1].split('function isNumberKey')[0].strip()[:-1]
		store_list = json.loads(self.fixLazyJson(data))['stores']
		link_list = response.xpath('//div[@id="curacaoLocations"]//div[@class="location"]//a/@href').extract()
		for cnt in range(0, len(store_list)):
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store_list[cnt]['storeName'])
				item['address'] = self.validate(store_list[cnt]['storeAddress'])
				item['city'] = self.validate(store_list[cnt]['storeCity'])
				item['state'] = self.validate(store_list[cnt]['storeState'])
				item['zip_code'] = self.validate(store_list[cnt]['storeZipCode'])
				item['country'] = 'United States'
				item['latitude'] = self.validate(str(store_list[cnt]['lat']))
				item['longitude'] = self.validate(str(store_list[cnt]['lng']))
				url = self.domain + self.validate(link_list[cnt])
				yield scrapy.Request(url=url, callback=self.parse_page, meta={'item':item})
			except:
				pdb.set_trace()		

	def parse_page(self, response):
		try:
			item = response.meta['item']
			detail = self.eliminate_space(response.xpath('//p[@class="address"]//text()').extract())
			for de in detail:
				if 'phone' in de.lower():
					item['phone_number'] = de.split(':')[1].strip()
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//p[@class="hours"]//text()').extract())
			for hour in hour_list[1:]:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			yield item
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip().replace('&#8211;','').replace(';','')
		except:
			return ''

	def format(self, item):
		try:
			return item.decode('UTF-8').strip()
		except:
			return ''

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item in state['name']:
				return state['country']
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