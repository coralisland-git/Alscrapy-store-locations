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

class rockport(scrapy.Spider):
	name = 'rockport'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://rockport.com.gotlocations.com/2016.index.php'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}

		for location in self.US_CA_States_list:
			formdata = {
				"bypass":"y",
				"lat2":"",
				"lon2":"",
				"c":"EN",
				"address":location['name'],
				"ip_country":location['country'],
				"rockportbrand":"1",
				"Submit":"search"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.body.split('L.marker')
		for store in store_list[1:]:
			try:
				store = store.split('var customIcon')[0].strip()
				tree = store.split("bindPopup('")[1].split("');")[0].strip()
				item = ChainItem()
				detail = self.eliminate_space(etree.HTML(tree).xpath('//text()'))
				if len(detail) == 3:
					item['store_name'] = detail[0]
					item['address'] = detail[1]
					try:
						item['city'] = self.validate(detail[2].split(',')[0])
						sz = self.validate(detail[2].split(',')[1]).split(' ')
						item['state'] = self.validate(sz[0])
						t_zip = ''
						for tmp in sz[1:]:
							t_zip += tmp + ' '
						item['zip_code'] = self.validate(t_zip)
					except:
						pdb.set_trace()
						item['state'] = self.validate(detail[2].split(' ')[0])
						item['zip_code'] = self.validate(detail[2].split(' ')[1])
				else:
					item['store_name'] = detail[0]
					item['address'] = detail[1]
					try:
						item['city'] = self.validate(detail[3].split(',')[0])
						sz = self.validate(detail[3].split(',')[1]).split(' ')
						item['state'] = self.validate(sz[0])
						t_zip = ''
						for tmp in sz[1:]:
							t_zip += tmp + ' '
						item['zip_code'] = self.validate(t_zip)
					except:
						pdb.set_trace()
						item['state'] = self.validate(detail[3].split(' ')[0])
						item['zip_code'] = self.validate(detail[3].split(' ')[1])
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = ''
				detail = etree.HTML(tree).xpath('//text()')
				for de in detail:
					if '-' in de:
						item['phone_number'] = self.validate(de.replace('phone:',''))
				item['latitude'] = store.split('], {')[0][2:].split(',')[0]
				item['longitude'] = store.split('], {')[0][2:].split(',')[1]
				if item['country'] == 'CA' or item['country'] == 'US':
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item
			except:
				pass


	def validate(self, item):
		try:
			return item.strip().replace('\\','').replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'miles' not in self.validate(item) and 'directions' not in self.validate(item) and 'phone' not in self.validate(item) and 'email' not in self.validate(item):
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
			if item != '':
				if item.lower() in state['abbreviation'].lower():
					return state['country']
		return ''

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''