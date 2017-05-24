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

class uniprix(scrapy.Spider):
	name = 'uniprix'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.uniprix.com/en/stores'
		yield scrapy.Request(url=init_url, callback=self.body)
		
	def body(self, response):
		city_list = self.eliminate_space(response.xpath('//div[contains(@class, "sitelocator_cities_suggestions")]//ul//li/text()').extract())
		url = 'https://www.uniprix.com/en/stores'
		for location in self.location_list:
			header = {
				"Accept":"text/html, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
				"X-Requested-With":"XMLHttpRequest"
			}
			formdata = {
				"lat":str(location['latitude']),
				"lng":str(location['longitude']),
				"search":"",
				"banners[]":"1",
				"banners[]":"241",
				"banners[]":"228"
			}
			yield scrapy.FormRequest(url=url, headers=header, formdata=formdata, method='post', callback=self.parse_page) 

	def parse_page(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="third-row cf pharmacy_details"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//span[@class="pharmacy"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//p[@class="address"]//a/text()').extract_first())
				address = self.validate(store.xpath('.//p[@class="address_rest"]//a/text()').extract_first())
				item['city'] = self.validate(address[:-7])
				item['zip_code'] = self.validate(address[-7:])
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store.xpath('.//p[contains(@class, "tel")]//a/text()').extract_first()).split('tel.')[1]
				h_temp = ''
				hour_list = store.xpath('.//div[contains(@class, "schedule")]//table//tr')
				for hour in hour_list:
					temp = self.eliminate_space(hour.xpath('.//text()').extract())
					for te in temp:
						h_temp += te + ' '
					h_temp += ', '
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item				
			except:
				pass

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