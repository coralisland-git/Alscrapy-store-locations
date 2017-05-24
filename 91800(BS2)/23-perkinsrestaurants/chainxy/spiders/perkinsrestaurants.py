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

class perkinsrestaurants(scrapy.Spider):
	name = 'perkinsrestaurants'
	domain = 'https://www.perkinsrestaurants.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			location_list = json.load(data_file)

	def start_requests(self):
		header = {
		'Accept':'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'en-US,en;q=0.8',
		'Connection':'keep-alive',
		'Content-Length':'0',
		'Content-Type':'application/json; charset=utf-8'
		}
		init_url  = 'http://www.perkinsrestaurants.com/wp-admin/admin-ajax.php?action=store_search&lat=35.149534&lng=-90.04898000000003&max_results=50&radius=25&autoload=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		# with open('response.html', 'wb') as f:
		# 	f.write(response.body)
		store_list = json.loads(response.body)
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['store'])
			item['store_number'] = store['id']
			item['address'] = store['address']
			item['address2'] = store['address2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip']
			item['country'] = store['country']
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
			yield item


	def validate(self, item):
		try:
			return item.replace(';','').strip()
		except:
			return ''