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

class tijuanaflats(scrapy.Spider):
	name = 'tijuanaflats'
	domain = 'https://tijuanaflats.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		
		for location in self.location_list:
			g = geocoder.google(location['name'])
			init_url = 'https://tijuanaflats.com/wp-admin/admin-ajax.php?action=store_search&lat='+str(g.latlng[0])+'&lng='+str(g.latlng[1])+'&max_results=100&radius=500'
			yield scrapy.Request(url=init_url, callback=self.body) 
		# yield scrapy.Request(url = 'https://tijuanaflats.com/wp-admin/admin-ajax.php?action=store_search&lat=27.3031142&lng=-92.8234278&max_results=100&radius=500', callback=self.body )


	def body(self, response):
		print("=========  Checking.......")
		if response.body != '':
			store_list = json.loads(response.body)
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['store'])
				item['store_number'] = store['id']
				item['address'] = self.validate(store['address'])
				item['address2'] = store['address2']
				item['city'] = store['city']
				item['state'] = store['state']
				item['zip_code'] = store['zip']
				item['country'] = 'United States'
				item['phone_number'] = store['phone']
				item['latitude'] = store['lat']
				item['longitude'] = store['lng']
				try:
					h_temp = ''
					hour_list = etree.HTML(store['hours']).xpath('//table//tr')
					for hour in hour_list:
						h_temp += hour.xpath('.//td[1]/text()')[0] + ' ' + hour.xpath('.//td[2]//time/text()')[0] + ', '
					item['store_hours'] = h_temp[:-2]
				except:
					item['store_hours'] = ''	
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if str(item['state']) not in self.history:
					yield item	

			self.history.append(str(item['state']))
					
	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''