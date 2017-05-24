import scrapy
import json
import csv
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

from selenium import webdriver
from lxml import html
import yaml
import re
import pdb

import tokenize
import token
from StringIO import StringIO

class menswearhouse(scrapy.Spider):
	
	name = 'menswearhouse'
	domain = 'https://www.menswearhouse.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url  = 'http://www.menswearhouse.com/StoreLocatorInventoryCheck?catalogId=12004&distance=50&langId=-1&storeId=12751&latlong=%s,%s' %(str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, callback=self.body) 
		yield scrapy.Request(url='http://www.menswearhouse.com/StoreLocatorInventoryCheck?catalogId=12004&distance=50&langId=-1&storeId=12751&latlong=18.220833,-66.590149', callback=self.body)

	def body(self, response):
		print("==================	 checking......")
		data = self.fixLazyJson(response.body)
		store_list = json.loads(data)['result']
		# pdb.set_trace()
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['address']['storeName'])
			item['store_number'] = store['address']['stlocId']
			item['address'] = self.validate(store['address']['address1'])
			item['address2'] = self.validate(store['address']['address2'])
			item['city'] = self.validate(store['address']['city'])
			item['state'] = store['address']['state']
			item['zip_code'] = store['address']['zipcode']
			item['country'] = store['address']['country']
			item['phone_number'] = store['address']['phone']
			item['latitude'] = store['address']['latlong'].split(',')[0]
			item['longitude'] = store['address']['latlong'].split(',')[1]
			h_temp = ''
			hour_list = store['address']['hours']
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item		

	def validate(self, item):
		try:
			return item.strip().replace('&#39','').replace(';','')
		except:
			return ''

	def fixLazyJson (self, in_text):
	        tokengen = tokenize.generate_tokens(StringIO(in_text).readline)

	        result = []
	        for tokid, tokval, _, _, _ in tokengen:
	            # fix unquoted strings
	            if (tokid == token.NAME):
	                if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
	                    tokid = token.STRING
	                    tokval = u'"%s"' % tokval

	            # fix single-quoted strings
	            elif (tokid == token.STRING):
	                if tokval.startswith ("'"):
	                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

	            # remove invalid commas
	            elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
	                if (len(result) > 0) and (result[-1][1] == ','):
	                    result.pop()

	            # fix single-quoted strings
	            elif (tokid == token.STRING):
	                if tokval.startswith ("'"):
	                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

	            result.append((tokid, tokval))

	        return tokenize.untokenize(result)
