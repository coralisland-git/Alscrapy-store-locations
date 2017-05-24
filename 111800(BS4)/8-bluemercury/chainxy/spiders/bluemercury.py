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
import pdb

class bluemercury(scrapy.Spider):
	name = 'bluemercury'
	domain = 'https://www.bluemercury.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://storc.brandingbrand.com/v1/stores/bluemercury?state=%s' % location['abbreviation']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['title']
			item['store_number'] = store['number']
			address = store['address'][0].split(',')
			if len(address) == 2:
				item['address'] = address[0]
				item['address2'] = ''
				c_temp = ''
				address = address[1].split(' ')
				for cnt in range(0, len(address)-2):
					c_temp += address[cnt] + ' '
				item['city'] = c_temp.strip()
				item['state'] = address[len(address)-2]
				item['zip_code'] = address[len(address)-1]
			else :
				item['address'] = address[0]
				item['address2'] = address[1]
				c_temp = ''
				address = address[2].split(' ')
				for cnt in range(0, len(address)-2):
					c_temp += address[cnt] + ' '
				item['city'] = c_temp.strip()
				item['state'] = address[len(address)-2]
				item['zip_code'] = address[len(address)-1]
			item['country'] = 'United States'
			# pdb.set_trace()
			try:
				item['phone_number'] = self.validate(store['services'][0]['contact']['phone']['local'])
			except:
				pass
			item['latitude'] = store['coords']['lat']
			item['longitude'] = store['coords']['lon']
			h_temp = ''
			hour_list = store['services'][0]['hours']['base']
			week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
			for week in week_list:
				if hour_list[week][0] != '':
					h_temp += week + ' ' + hour_list[week][0] + '-' + hour_list[week][1] + ', ' 
			try:
				item['store_hours'] = h_temp[:-2]
			except:
				item['store_hours'] = ''
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_name']+str(item['store_number']) not in self.history:
				self.history.append(item['store_name']+str(item['store_number']))
				yield item		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''