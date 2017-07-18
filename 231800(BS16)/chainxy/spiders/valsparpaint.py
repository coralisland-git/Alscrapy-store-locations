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

class valsparpaint(scrapy.Spider):
	name = 'valsparpaint'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://hosted.where2getit.com/valspar/ajax?&xml_request='
			payload = '<request><appkey>2E81360E-8DB7-11E3-B631-FB93407E493E</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>10000</limit><atleast>50</atleast><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude></geoloc></geolocs><searchradius>10|25|50|100</searchradius><where><valspar_paint><eq>Y</eq></valspar_paint></where></formdata></request>'
			yield scrapy.Request(url=init_url + payload, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//poi')
		for store in store_list:
			try:
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
				uid = self.validate(store.xpath('.//uid/text()'))
				if uid not in self.history:
					self.history.append(uid)
					yield item		
			except:
				pass

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''