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

class lcbo(scrapy.Spider):
	name = 'lcbo'
	domain = 'https://www.lcbo.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url  = 'http://www.lcbo.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?catalogId=10001&langId=-1&orderId=&storeId=10151'
			header = {
				'Accept':'*/*',
				'Accept-Encoding':'gzip, deflate',
				'Content-Type':'application/x-www-form-urlencoded',
				'Host':'www.lcbo.com',
				'Origin':'http://www.lcbo.com',
				'X-Requested-With':'XMLHttpRequest',
			}
			form_data = {
				'fromPage':'StoreLocator',
				'features':'',
				'dayOfWeek':'',
				'closeHour':'',
				'citypostalcode':location['city'].split(' (')[0],
				'latitude':'',
				'longitude':'',
				'ageChecked':'[object Event]',
				'objectId':'',
				'requesttype':'ajax'
			}
			yield scrapy.FormRequest(url=init_url,formdata=form_data, method='POST', headers=header, callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="row store-details"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-name"]/text()'))
			item['store_number'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-name"]/text()')).split('#')[1].strip()
			item['address'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-street-address"]/text()')) +  self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-street-address"]//div/text()'))
			item['address2'] = ''
			item['city'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-city"]/text()'))
			item['state'] = ''
			item['zip_code'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-postal"]/text()'))
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(store.xpath('.//div[@class="store-address"]//div[@class="store-phone"]/text()'))
			item['latitude'] = ''
			item['longitude'] = ''
			h_temp = ''
			hour_list = store.xpath('.//ul[@class="hours-list"]//li')
			for hour in hour_list:
				h_temp = h_temp + self.validate(hour.xpath('.//span[@class="weekday"]/text()')) + ' ' + self.validate(hour.xpath('.//span[@class="open-time"]/text()')) + ' - ' + self.validate(hour.xpath('.//span[@class="close-time"]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if h_temp == '':
				item['coming_soon'] = '1'
			if item['store_number'] not in self.history:
				yield item
				self.history.append(item['store_number'])

	def validate(self, item)			:
		try:
			return item.extract_first().strip()
		except:
			return ''			
