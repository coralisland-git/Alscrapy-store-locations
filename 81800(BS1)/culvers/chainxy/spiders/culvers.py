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

class culvers(scrapy.Spider):
	name = 'culvers'
	domain = 'https://www.culvers.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
	def start_requests(self):
		for location in self.location_list:
			payload = '<request><appkey>1099682E-D719-11E6-A0C4-347BDEB8F1E5</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><stateonly>1</stateonly><geolocs><geoloc><addressline>'+location['city']+', '+ location['state']+'</addressline><longitude></longitude><latitude></latitude><country></country></geoloc></geolocs><searchradius>250</searchradius></formdata></request>'
			yield scrapy.Request(url='https://hosted.where2getit.com/crackerbarrel/ajax?lang=en_US&xml_request=%s' % payload, callback=self.body)

	def body(self, response):
		store_list = response.xpath('//collection//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['store_number'] = self.validate(store.xpath('.//number/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			h_temp = 'Monday : ' + self.validate(store.xpath('.//monopenfrom/text()')) + '-' + self.validate(store.xpath('.//monopento/text()'))
			h_temp = h_temp + ', Thuesday : ' + self.validate(store.xpath('.//tuesopenfrom/text()')) + '-' + self.validate(store.xpath('.//tuesopento/text()'))
			h_temp = h_temp + ', Wednesday : ' + self.validate(store.xpath('.//wedopenfrom/text()')) + '-' + self.validate(store.xpath('.//wedopento/text()'))
			h_temp = h_temp + ', Thursday : ' + self.validate(store.xpath('.//thursopenfrom/text()')) + '-' + self.validate(store.xpath('.//thursopento/text()'))
			h_temp = h_temp + ', Friday : ' + self.validate(store.xpath('.//friopenfrom/text()')) + '-' + self.validate(store.xpath('.//friopento/text()'))
			h_temp = h_temp + ', Saturday : ' + self.validate(store.xpath('.//satopenfrom/text()')) + '-' + self.validate(store.xpath('.//satopento/text()'))
			h_temp = h_temp + ', Sunday : ' + self.validate(store.xpath('.//sunopenfrom/text()')) + '-' + self.validate(store.xpath('.//sunopento/text()'))
			item['store_hours'] = h_temp
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if 'Coming Soon' in item['store_name']:
				item['coming_soon'] = '1'
			if item['store_name']+str(item['store_number']) not in self.history:
				yield item
				self.history.append(item['store_name']+str(item['store_number']))

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''