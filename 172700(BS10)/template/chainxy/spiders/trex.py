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

class trex(scrapy.Spider):
	name = 'trex'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/geocode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.trex.com/find-trex/dealer-locator/?distance=200&Searchcountry=US&Searchlatitude='+str(location['latitude'])+'&Searchlongitude='+str(location['longitude'])+'&miles=200'
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, sdch"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "find-trex-result-column")][1]//ol[@class="results"]//li//div[contains(@class, "result_info")]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h5/text()').extract_first())
			address_temp = self.eliminate_space(store.xpath('.//p[@class="distance"][2]//text()').extract())
			address = ''
			for temp in address_temp:
				address += temp + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div/text()').extract_first())
			if item['address'] + item['phone_number'] not in self.history:
				self.history.append(item['address'] + item['phone_number'])
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
