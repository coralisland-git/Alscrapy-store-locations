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

class bostonpizza(scrapy.Spider):
	name = 'bostonpizza'
	domain = 'https://www.bostonpizza.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://bostonpizza.com/json/stores-en.json'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['id']
			item['address'] = store['address']['address']
			item['address2'] = ''
			item['city'] = store['address']['city']
			item['state'] = store['address']['province']
			item['zip_code'] = store['address']['postal_code']
			item['country'] = store['address']['country']
			item['phone_number'] = store['contact']['store']
			item['latitude'] = store['coordinates']['latitude']
			item['longitude'] = store['coordinates']['longitude']
			h_temp = ''
			hour_list = store['hours']
			for hour in hour_list:
				h_temp += hour + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''