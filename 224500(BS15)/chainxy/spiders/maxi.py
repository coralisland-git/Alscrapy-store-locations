from __future__ import unicode_literals
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

class maxi(scrapy.Spider):
	name = 'maxi'
	domain = 'http://www.maxi.ca'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.maxi.ca/en_CA/store-list-page.QC.html'
		yield scrapy.Request(url=init_url, callback=self.body)		

	def body(self, response):
		self.driver.get("http://www.maxi.ca/en_CA/store-list-page.QC.html")
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		city_list = tree.xpath('//ul[@class="store-select"]//a/@href')
		for city in city_list:
			city = city.split('QC.')[1].split('.')[0].strip()
			link = 'http://www.maxi.ca/banners/store/v1/listing/maxi?lang=en_CA&banner=24&banner=25&proximity=75&city='+city+'&province=QC'
			header = {
				"Accept":"*/*",
				"Accept-Encoding":"gzip, deflate, sdch",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=link, headers=header, method='get', callback=self.parse_page)

	def parse_page(self, response):
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['storeName'])
				item['store_number'] = self.validate(store['storeNumber'])
				item['address'] = self.validate(store['address']['addressLine1'])
				item['address2'] = self.validate(store['address']['addressLine2'])
				item['city'] = self.validate(store['address']['city'])
				item['state'] = self.validate(store['address']['province'])
				item['zip_code'] = self.validate(store['address']['postalCode'])
				item['country'] = self.validate(store['address']['country'])
				item['phone_number'] = self.validate(store['phoneNumber'])
				item['latitude'] = self.validate(str(store['address']['latitude']))
				item['longitude'] = self.validate(str(store['address']['longitude']))

				h_temp = ''
				for hour in store['operatingHours']:
					h_temp += hour['day'] + ' ' + hour['hours'] + ', '
				item['store_hours'] = h_temp[:-2]
				yield item	
			except:
				pass		

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp