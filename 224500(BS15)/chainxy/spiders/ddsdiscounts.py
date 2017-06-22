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
import pdb

class ddsdiscounts(scrapy.Spider):
	name = 'ddsdiscounts'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://hosted.where2getit.com/ddsdiscounts/ajax?&xml_request='
			payload = '<request><appkey>001E3698-16B1-11E5-9795-B2D20C516365</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>25|50|100|250|500|800|1000|1500|2000</searchradius><where><or><opendate><eq></eq></opendate><annoucements><eq></eq></annoucements></or></where></formdata></request>'
			url = init_url + payload
			yield scrapy.Request(url=url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
			h_temp = ''
			for week in week_list:
				h_temp += week.upper() + ' ' + self.validate(store.xpath('.//'+week+'/text()')) +', '
			item['store_hours'] = h_temp[:-2]
			uid = self.validate(store.xpath('.//uid/text()'))
			if uid not in self.history:
				self.history.append(uid)
				yield item		

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''