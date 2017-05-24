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

class ezmart(scrapy.Spider):
	name = 'ezmart'
	domain = ''
	history = []

	def start_requests(self):
		self.init_url = 'http://e-zmart.com/ajaxpro/StationWebsites.SharedContent.Web.Common.Controls.Map.StoreData,StationWebsites.ashx'
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'text/plain; charset=UTF-8',
			'X-AjaxPro-Method':'GetStatePins'
		}
		payload= {
			'srl':{
					"MaxLat":"42.58544647363446",
					"MaxLong":"-80.17722718749997",
					"MinLat":"24.206892367830076",
					"MinLong":"-110.49949281249997",
					"ZoomLevel":"5"
				}
		}
		yield scrapy.Request(url=self.init_url, body=json.dumps(payload), headers=header, method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'text/plain; charset=UTF-8',
			'X-AjaxPro-Method':'GetStorePins'
		}
		location_list = json.loads(response.body)['value']['Payload']
		for location in location_list:
			payload= {
			'pinType':'1',
			'srl':{
					"MaxLat":str(float(location['Point']['Latitude'])+3.2),
					"MaxLong":str(float(location['Point']['Longitude'])+3.4),
					"MinLat":str(float(location['Point']['Latitude'])-2.25),
					"MinLong":str(float(location['Point']['Longitude'])-2.5),
					"ZoomLevel":"7"
				}
			}
			yield scrapy.Request(url=self.init_url, body=json.dumps(payload), headers=header, method='post', callback=self.parse_store) 

	def parse_store(self, response):

		print("=========  Checking.......")
		store_list = json.loads(response.body)['value']['Payload']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['Store']['DisplayName'])
			item['store_number'] = self.validate(str(store['Store']['ID']))
			item['address'] = self.validate(store['Store']['Address'])
			item['city'] = self.validate(store['Store']['City'])
			item['state'] = self.validate(store['Store']['State'])
			item['zip_code'] = self.validate(store['Store']['Zip'])
			item['country'] = self.validate(store['Store']['Country'])
			item['phone_number'] = self.validate(store['PrimaryPhoneNumber'])
			item['latitude'] = self.validate(str(store['Store']['Latitude']))
			item['longitude'] = self.validate(str(store['Store']['Longitude']))
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''