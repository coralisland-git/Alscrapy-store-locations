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

class test(scrapy.Spider):
	name = 'test'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://citizenwatch.com.gotlocations.com/index.php'

		for location in self.location_list:
			formdata = {
				'c': 'IE',
				'ip_country': 'US',
				'address': location['abbreviation'],
				'bypass': 'y',
				'Submit': 'search',
				'lat2': '',
				'lon2': ''
			}
			headers = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate",
				"Content-Type": "application/x-www-form-urlencoded"
			}
			yield scrapy.FormRequest(url=init_url, method="POST", headers=headers, formdata=formdata, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//div[contains(@class, "altrow")]')
		for store in store_list:
			item = ChainItem()
			detail = self.eliminate_space(store.xpath('.//text()').extract())
			item['store_name'] = self.validate(detail[0])
			address = ''
			item['phone_number'] = ''
			for de in detail:
				if 'phone' in de:
					item['phone_number'] = self.validate(de.split(':')[1])
					break
				else:
					address += de + ', '
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
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'drive' not in self.validate(item.lower()) and 'about' not in self.validate(item.lower()):
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

