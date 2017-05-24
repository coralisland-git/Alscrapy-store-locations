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

class tommyhilfiger(scrapy.Spider):
	name = 'tommyhilfiger'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://global.tommy.com/int/en/stores/find-a-store/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		country_list = response.xpath('//select[@id="storecountry"]//option/@value').extract()
		for country in country_list:
			url = 'http://global.tommy.com/int/en/stores/find-a-store/9?storecountry='+country+'&storecity=&product='
			yield scrapy.Request(url=url, callback=self.parse_page, meta={'country':country})

	def parse_page(self, response):
		store_list = response.xpath('//div[@class="tommy-list stores"]//li//div[@class="store-info"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h1/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//dd[@class="street"]/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//dd[@class="location"]/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//dd[@class="location"]/text()').extract_first().split(',')[0])
				item['country'] = self.validate(store.xpath('.//dd[@class="location"]/text()').extract_first().split(',')[1])
				item['phone_number'] = self.validate(store.xpath('.//dd[@class="phone"]/text()').extract_first())
				item['store_hours'] = self.validate(store.xpath('.//dd[@class="hours"]/text()').extract_first())
				yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\r', '').replace('\t','').replace(';','')
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
