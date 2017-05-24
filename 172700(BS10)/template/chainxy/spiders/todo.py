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

class todo(scrapy.Spider):
	name = ''
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = ''
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = json.loads(response.body)
		pdb.set_trace()
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(store['store_number'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address2'])
			
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += temp[0].replace(',', '') + ' '

			address = ''
			addr = address.split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			h_temp = ''
			hour_list = ''
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_hours'] = self.validate(store['hours'])
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			


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
