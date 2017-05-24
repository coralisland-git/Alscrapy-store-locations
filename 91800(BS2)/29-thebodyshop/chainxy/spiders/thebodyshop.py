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

class thebodyshop(scrapy.Spider):
	name = 'thebodyshop'
	domain = 'https://www.thebodysho.com/'

	def start_requests(self):
		country_list = ['US', 'CA']
		for country in country_list:
			init_url  = 'https://www.thebodyshop.com/en-us/store-finder/search?country='+country
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = ''
			item['address'] = store['address']
			item['address2'] = store['address2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip']
			item['country'] = store['country']['name']
			item['phone_number'] = store['number']
			item['latitude'] = ''
			item['longitude'] = ''
			try:
				item['store_hours'] = 'Mon ' + store['open']['mo'][0] + ' - ' + store['open']['mo'][1] 
				item['store_hours'] += ', Tue ' + store['open']['tu'][0] + ' - ' + store['open']['tu'][1]
				item['store_hours'] += ', Wed ' + store['open']['we'][0] + ' - ' + store['open']['we'][1]
				item['store_hours'] += ', Thu ' + store['open']['th'][0] + ' - ' + store['open']['th'][1]
				item['store_hours'] += ', Fri ' + store['open']['fr'][0] + ' - ' + store['open']['fr'][1]
				item['store_hours'] += ', Sat ' + store['open']['sa'][0] + ' - ' + store['open']['sa'][1]
				item['store_hours'] += ', Sun ' + store['open']['su'][0] + ' - ' + store['open']['su'][1]
			except:
				item['store_hours'] = ''
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item	

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''