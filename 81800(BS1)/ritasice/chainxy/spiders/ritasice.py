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
import geocoder

class ritasice(scrapy.Spider):
	name = 'ritasice'
	domain = 'https://www.ritasice.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.ritasice.com/wp-admin/admin-ajax.php'

		header = {
		'X-Requested-With':'XMLHttpRequest'
		}
		for location in self.location_list:

			try:
				form_data = {
					'address':location['city'],
					'formdata':'nameSearch=&addressInput='+location['city'],
					'lat':str(location['latitude']),
					'lng':str(location['longitude']),
					'name':'',
					'radius':'1000',
					'tags':'',
					'action':'csl_ajax_search',
				}
			except:
				g = geocoder.google(location['city'])
				form_data = {
					'address':location['city'],
					'formdata':'nameSearch=&addressInput='+location['city'],
					'lat':str(g.latlng[0]),
					'lng':str(g.latlng[1]),
					'name':'',
					'radius':'1000',
					'tags':'',
					'action':'csl_ajax_search',
				}
			
			yield scrapy.FormRequest(url=init_url, formdata=form_data, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = json.loads(response.body)
		store_list = data['response']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.eliminater(store['name']).split('(')[0].strip()
				item['store_number'] = self.eliminater(store['name']).split('(')[1][:-1]
				item['address'] = self.eliminater(store['address']).strip()
				item['address2'] = self.eliminater(store['address2']).strip()
				item['city'] = store['city']
				item['state'] = store['state']
				item['zip_code'] = store['zip']
				try:
					zipcode = int(item['zip_code'])
					item['country'] = 'United States'
				except:
					item['country'] = 'Canada'
				
				item['phone_number'] = store['phone']
				item['latitude'] = store['lat']
				item['longitude'] = store['lng']
				hour_list = store['hours'].split(';')
				h_temp = ''
				if len(hour_list) > 2:
					h_temp = self.convert(hour_list[4]) + ' : ' + self.convert(hour_list[10])
					cnt = 16
					for num in range(1,7):
						if hour_list[cnt+6] == 'closed':
							h_temp = 'closed'
						else:
							h_temp = h_temp + ', ' + self.convert(hour_list[cnt]) + ' : ' + self.convert(hour_list[cnt+6])
						cnt = cnt + 12
				item['store_hours'] = h_temp
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = '0'
				if 'COMING SOON' in item['store_name']:
					item['coming_soon'] = '1'
				if item['store_name']+str(item['store_number']) not in self.history:
					yield item
					self.history.append(item['store_name']+str(item['store_number']))
			except:
					pass
		

	def convert(self, item):
		return item.split('&')[0]

	def eliminater(self, item):
		return item.replace('&amp;', ' ').replace('&#039;', ' ')