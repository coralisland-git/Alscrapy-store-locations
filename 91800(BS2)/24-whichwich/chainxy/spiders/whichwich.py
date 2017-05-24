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

class whichwich(scrapy.Spider):
	name = 'whichwich'
	domain = 'https://www.whichwich.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url  = 'https://www.whichwich.com/locations/'
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded',
			'Referer':'https://www.whichwich.com/locations/'
		}
		for location in self.location_list:
			form_data = {
				'search': location['city'],
				'sub':'search'
			}
			request = scrapy.FormRequest(url=init_url,formdata=form_data, method='POST', headers=header, callback=self.body)
			request.meta['city'] = location['city']
			request.meta['state'] = location['state']
			yield request

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="right-container"]//div[@class="single-result"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = ''
			item['store_number'] = ''
			item['address'] = self.validate(store.xpath('.//div[2]//p/text()'))
			item['address2'] = ''
			item['city'] = self.validate(store.xpath('.//div[1]//h3/text()'))
			item['state'] = response.meta['state']
			item['zip_code'] = ''
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[3]//p/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			item['store_hours'] = self.validate(store.xpath('.//div[@class="hours"]//p/text()'))
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['phone_number'] in self.history:
				continue
			self.history.append(item['phone_number'])
			yield item	


	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''