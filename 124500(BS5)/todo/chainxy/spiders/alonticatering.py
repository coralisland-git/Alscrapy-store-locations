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

class alonticatering(scrapy.Spider):
	name = 'alonticatering'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/TX_CA_IL_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.alonti.com/menu/catering_menu'
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded'
		}
		for location in self.location_list:
			formdata = {
				'zipcode':str(location['zipcode'])
			}
			yield scrapy.FormRequest(url=init_url, headers=header, method='POST', formdata=formdata, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		item = ChainItem()
		try:
			detail = response.xpath('//div[contains(@class, "orange-box")]//p//text()').extract()
			item['store_name'] = self.validate(detail[0]).strip()[1:]
			if ',' in item['store_name']:
				item['store_number'] = item['store_name'].split(',')[0].strip()
				item['store_name'] = item['store_name'].split(',')[1].strip()
			else: 
				item['store_number'] = item['store_name'][:2].strip()
				item['store_name'] = item['store_name'][2:].strip()
			address = detail[2] + ', ' + detail[3]
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

			item['phone_number'] = self.validate(detail[4]).split('Phone:')[1].strip()
			if item['store_name'] not in self.history:
				self.history.append(item['store_name'])
				yield item
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''