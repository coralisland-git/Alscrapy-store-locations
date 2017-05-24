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

class crackerbarrel(scrapy.Spider):
	name = 'crackerbarrel'
	domain = 'https://www.crackerbarrel.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
	def start_requests(self):
		for location in self.location_list:
			payload = '<request><appkey>3C44AEBA-B85D-11E5-B8DC-C8188E89CD5A</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>'+location['city']+', '+ location['state']+'</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>200</searchradius><where><openingsoon><eq>0</eq></openingsoon><labslocation><eq>null</eq></labslocation></where></formdata></request>'
			yield scrapy.Request(url='https://hosted.where2getit.com/crackerbarrel/ajax?lang=en_US&xml_request=%s' % payload, callback=self.body)

	def body(self, response):
		store_list = response.xpath('//collection//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['store_number'] = self.validate(store.xpath('.//uid/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			h_temp = 'Sunday - Thursday : ' + self.validate(store.xpath('.//saturday_open/text()')) + '-' + self.validate(store.xpath('.//saturday_close/text()'))
			h_temp = h_temp + ', Friday - Saturday' + self.validate(store.xpath('.//friday_open/text()')) + '-' + self.validate(store.xpath('.//friday_close/text()'))
			item['store_hours'] = h_temp
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_name']+str(item['store_number']) not in self.history:
				yield item
				self.history.append(item['store_name']+str(item['store_number']))

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''