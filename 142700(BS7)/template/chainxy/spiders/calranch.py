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
import tokenize
import token
from StringIO import StringIO

class calranch(scrapy.Spider):
	handle_httpstatus_list = [400]
	name = 'calranch'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.calranch.com/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=40.6096698&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=-111.9391031&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=region_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=region&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bvalue%5D=10000&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=onlyLocation&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=30'
		# init_url = 'https://www.calranch.com/rest/V1/storelocator/search/?'
		header={
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate, sdch, br',
			'X-Requested-With':'XMLHttpRequest',
			'Host':'www.calranch.com',
			'Referer':'https://www.calranch.com/storelocator/',
			'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
		}
		payload = {
			"searchCriteria[filter_groups][0][filters][0][field]":"lat",
			"searchCriteria[filter_groups][0][filters][0][value]":"40.6096698",
			"searchCriteria[filter_groups][0][filters][0][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][1][field]":"lng",
			"searchCriteria[filter_groups][0][filters][1][value]":"-111.9391031",
			"searchCriteria[filter_groups][0][filters][1][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][2][field]":"country_id",
			"searchCriteria[filter_groups][0][filters][2][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][3][field]":"region_id",
			"searchCriteria[filter_groups][0][filters][3][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][4][field]":"region",
			"searchCriteria[filter_groups][0][filters][4][value]":"Los angeles",
			"searchCriteria[filter_groups][0][filters][4][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][5][field]":"distance",
			"searchCriteria[filter_groups][0][filters][5][value]":"500",
			"searchCriteria[filter_groups][0][filters][5][condition_type]":"eq",
			"searchCriteria[filter_groups][0][filters][6][field]":"onlyLocation",
			"searchCriteria[filter_groups][0][filters][6][value]":"0",
			"searchCriteria[filter_groups][0][filters][6][condition_type]":"eq",
			"searchCriteria[current_page]":"1",
			"searchCriteria[page_size]":"30"
		}

		yield scrapy.Request(url=init_url, headers=header, method='GET', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['items']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['address'] = self.validate(store['street'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['region'])
			item['zip_code'] = self.validate(store['postal_code'])
			item['country'] = self.validate(store['country_id'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			yield item			


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
