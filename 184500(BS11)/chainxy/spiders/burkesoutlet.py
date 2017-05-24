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

class burkesoutlet(scrapy.Spider):
	name = 'burkesoutlet'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.burkesoutlet.com/StoreLocator/GetMarkers'

		header = {
			"accept":"application/json, text/plain, */*",
			"accept-encoding":"gzip, deflate, br",
			"content-type":"application/json;charset=UTF-8",
			"x-newrelic-id":"UwQHWFZUGwIBVVBQBAcO"
					}
		payload = {

		}
		# formdata = {

		# }

		# yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)
		# yield scrapy.Request(url=init_url, body=json.dumps(payload), headers=header,callback=self.body)
		
		yield scrapy.Request(url=init_url, headers=header, method='post', body=json.dumps(payload), callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)
		# store_list = json.loads(response.body)['model']['Markers']
		# print("=========  Checking.......", len(store_list))
		# for store in store_list:
		# 	try:
		# 		item = ChainItem()
		# 		detail = self.eliminate_space(store.xpath())
		# 		item['store_name'] = self.validate(store['name'])
		# 		item['store_number'] = self.validate(store['store_number'])
		# 		item['address'] = self.validate(store['address'])
		# 		item['address2'] = self.validate(store['address2'])
				
		# 		address = ''
		# 		item['address'] = ''
		# 		item['city'] = ''
		# 		addr = usaddress.parse(address)
		# 		for temp in addr:
		# 			if temp[1] == 'PlaceName':
		# 				item['city'] += temp[0].replace(',','')	+ ' '
		# 			elif temp[1] == 'StateName':
		# 				item['state'] = temp[0].replace(',','')
		# 			elif temp[1] == 'ZipCode':
		# 				item['zip_code'] = temp[0].replace(',','')
		# 			else:
		# 				item['address'] += temp[0].replace(',', '') + ' '

		# 		address = ''
		# 		addr = address.split(',')
		# 		item['city'] = self.validate(addr[0].strip())
		# 		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		# 		item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

		# 		item['city'] = self.validate(store['city'])
		# 		item['state'] = self.validate(store['state'])
		# 		item['zip_code'] = self.validate(store['zip'])
		# 		item['country'] = self.validate(store['country'])
		# 		item['phone_number'] = self.validate(store['phone'])
		# 		item['latitude'] = self.validate(store['latitude'])
		# 		item['longitude'] = self.validate(store['longitude'])

		# 		h_temp = ''
		# 		hour_list = ''
		# 		for hour in hour_list:
		# 			h_temp += hour + ', '
		# 		item['store_hours'] = h_temp[:-2]

		# 		item['store_hours'] = self.validate(store['hours'])
		# 		item['store_type'] = ''
		# 		item['other_fields'] = ''
		# 		item['coming_soon'] = ''
		# 		if item['store_number'] not in self.history:
		# 			self.history.append(item['store_number'])
		# 			yield item	
		# 	except:
		# 		pdb.set_trace()		


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