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

class petsuppliesplus(scrapy.Spider):
	name = 'petsuppliesplus'
	domain = 'https://www.petsuppliesplus.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.petsuppliesplus.com/api/sitecore/Store/GetNextStores'
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest',
		}
		form_data = {
			"onPage":"26",
			"radiusInMiles":"50",
			"searchFlag":"1"
		}
		yield scrapy.FormRequest(url=init_url, formdata=form_data, headers=header, method='POST', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		with open('response-pet.html', 'wb') as f:
			f.write(response.body)
		# store_list = json.loads(response.body)
		# for store in store_list:
		# 	item = ChainItem()
		# 	item['store_name'] = store['Name']
		# 	item['store_number'] = store['MyStoreID']
		# 	item['address'] = store['Address1']
		# 	item['address2'] = store['Address2']
		# 	item['city'] = store['City']
		# 	item['state'] = store['StateCode']
		# 	item['zip_code'] = store['Zip']
		# 	item['country'] = 'Canada'
		# 	item['phone_number'] = store['Phone']
		# 	item['latitude'] = store['LatPos']
		# 	item['longitude'] = store['LngPos']
		# 	item['store_hours'] = ''
		# 	item['store_type'] = ''
		# 	item['other_fields'] = ''
		# 	item['coming_soon'] = ''
		# 	if item['store_number'] in self.history:
		# 		continue
		# 	self.history.append(item['store_number'])
		# 	yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''