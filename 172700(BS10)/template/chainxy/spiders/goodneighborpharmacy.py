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

class goodneighborpharmacy(scrapy.Spider):
	name = 'goodneighborpharmacy'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://abdc.force.com/StoreLocatorResponse?lat='+str(location['latitude'])+'&lng='+str(location['longitude'])+'&rowsPerPage=250&callback=jsonpcallback&_=1495149127857'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('jsonpcallback(')[1].strip()[:-1]
			store_list = json.loads(data)['data']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['account_dba_name'])
				item['address'] = self.validate(store['business_street_address'])
				item['city'] = self.validate(store['business_address_city'])
				item['state'] = self.validate(store['business_address_state'])
				item['zip_code'] = self.validate(store['business_address_zip_code'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['consumer_phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				h_temp = ''
				if self.validate(store['gnp_web_hours_store']) != '':
					h_temp = 'Store Hours : ' + self.validate(store['gnp_web_hours_store'])
				if self.validate(store['gnp_web_hours_rx']) != '':
					h_temp +=' Pharmacy Hours : ' + self.validate(store['gnp_web_hours_rx'])
				item['store_hours'] = h_temp[:-1]
				if item['phone_number'] not in self.history:
					self.history.append(item['phone_number'])
					yield item			
		except:
			pass


	def validate(self, item):
		try:
			return item.strip().replace(';',',').replace('&amp;',',').replace('\n','').replace('\r','')
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
