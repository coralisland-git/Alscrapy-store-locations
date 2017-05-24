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


class threedogbakery(scrapy.Spider):
	name = 'threedogbakery'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/2180/stores.js?callback=storeMapperCallback2'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		
		store_list = json.loads(response.body.split('storeMapperCallback2(')[1].strip()[:-1])['stores']
		for store in store_list:
			url = etree.HTML('<div>'+ self.validate(store['custom_field_1']) + '</div>').xpath('//div//a/@href')[0]
			request = scrapy.Request(url=url, callback=self.parse_page)
			request.meta['store_name'] = self.validate(store['name'])
			request.meta['store_number'] = self.validate(str(store['id']))
			request.meta['address'] = ''
			request.meta['city'] = ''
			request.meta['country'] = ''

			address = self.validate(store['address'])
			if 'canada' in address.lower():
				addr = address.split(',')
				request.meta['address'] = addr[0]
				request.meta['city'] = addr[1]
				request.meta['state'] = ''
				request.meta['zip_code'] = ''
				sz_temp = addr[2].split(' ')
				for sz in sz_temp:
					if len(sz) == 3:
						request.meta['zip_code'] += sz + ' '
					else:
						request.meta['state'] += sz + ' '
				request.meta['country'] = 'Canada'

			else:
				request.meta['country'] = 'United States'
				if 'Hong Kong' in address:
					request.meta['country'] = 'Hong Kong'
					address = address.replace('Hong Kong','')

				address = address.replace('United','').replace('States','')
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						request.meta['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						request.meta['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						request.meta['zip_code'] = temp[0].replace(',','')
					else:
						request.meta['address'] += temp[0].replace(',', '') + ' '
				
			request.meta['phone_number'] = self.validate(store['phone'])
			request.meta['latitude'] = self.validate(str(store['latitude']))
			request.meta['longitude'] = self.validate(str(store['longitude']))
			yield request

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = response.meta['store_name']
		item['store_number'] = response.meta['store_number']
		try:
			item['address'] = response.meta['address']
		except:
			pass
		try:
			item['city'] = response.meta['city']
		except:
			pass
		try:
			item['state'] = response.meta['state']
		except:
			pass
		try:
			item['zip_code'] = response.meta['zip_code']
		except:
			pass
		try:
			item['country'] = response.meta['country']
		except:
			pass
		item['phone_number'] = response.meta['phone_number']
		item['latitude'] = response.meta['latitude']
		item['longitude'] = response.meta['longitude']
		h_temp = ''
		hour_list = self.eliminate_space(response.xpath('//div[@class="BlockContent PageContent"]//text()').extract())
		for hour in hour_list:
			if 'am' in hour.lower() and 'pm' in hour.lower():
				h_temp += self.validate(hour) + ', '
		item['store_hours'] = h_temp[:-2]
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
