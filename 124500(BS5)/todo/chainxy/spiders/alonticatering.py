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
		detail = response.xpath('//div[contains(@class, "orange-box")]//p/text()').extract()
		item['store_name'] = self.validate(detail[0]).split(',')[1].strip()
		item['store_number'] = self.validate(detail[0]).split(',')[0].strip()[1:]
		item['address'] = self.validate(detail[2])
		addr = self.validate(detail[3]).split(',')
		item['city'] = self.validate(addr[0].strip())
		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
		item['phone_number'] = self.validate(detail[4]).split('Phone:')[1].strip()
		if item['store_name'] not in self.history:
			self.history.append(item['store_name'])
			yield item

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''