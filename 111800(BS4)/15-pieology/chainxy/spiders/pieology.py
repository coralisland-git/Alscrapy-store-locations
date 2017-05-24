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

class pieology(scrapy.Spider):
	name = 'pieology'
	domain = 'http://www.pieology.com/'
	history = []


	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://momentfeed-prod.apigee.net/api/llp.json?auth_token=DGUFODSRWUFNBBIQ&coordinates='+str(location['latitude']-3)+','+str(location['longitude']+3)+','+str(location['latitude']+3)+','+str(location['longitude']-3)+'&pageSize=50'
			yield scrapy.Request(url=init_url, callback=self.body) 
	def body(self, response):
		print("=========  Checking.......")
		# with open('response.html', 'wb') as f:
		# 	f.write(response.body)

		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = store['store_info']['name']
				item['coming_soon'] = '0'
				if '-' in store['store_info']['name']:
					item['store_name'] = store['store_info']['name'].split('-')[0].strip()
					item['coming_soon'] = '1'
				item['store_number'] = store['store_info']['corporate_id']
				item['address'] = store['store_info']['address']
				item['address2'] = store['store_info']['address_extended']
				item['city'] = store['store_info']['locality']
				item['state'] = store['store_info']['region']
				item['zip_code'] = store['store_info']['postcode']
				item['country'] = store['store_info']['country']
				item['phone_number'] = store['store_info']['phone']
				item['latitude'] = store['store_info']['latitude']
				item['longitude'] = store['store_info']['longitude']
				h_temp = ''
				week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
				hour_list = store['store_info']['store_hours'].split(';')
				try:
					for hour in hour_list:
						time = hour.split(',')
						h_temp += week_list[int(time[0])-1] + ' ' + time[1][:2] + ':' + time[1][2:] + '-' + time[2][:2] + ':' + time[2][2:] + ', '
				except :
					pass
				item['store_hours'] = h_temp[:-2]
				item['store_type'] = ''
				item['other_fields'] = ''
				
				if item['store_name']+str(item['store_number']) not in self.history:
					self.history.append(item['store_name']+str(item['store_number']))
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''