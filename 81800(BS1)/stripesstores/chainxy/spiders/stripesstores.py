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

class stripesstores(scrapy.Spider):
	name = 'stripesstores'
	domain = 'http://stripesstores.com/'
	history = ['']

	def start_requests(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		init_url  = 'http://hosted.where2getit.com/stripesstores/ajax?lang=es_US&xml_request='
		with open(file_path) as data_file:    
		    location_list = json.load(data_file)
		for location in location_list:
			payload = '<request><appkey>DA4883E0-A4AD-11E3-B795-4F47D1784D66</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>'+location['city']+', '+ location['state']+'</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>1000</searchradius><where><laredo_taco><eq></eq></laredo_taco><truck_accessible><eq></eq></truck_accessible><carwash><eq></eq></carwash><atm><eq></eq></atm><lube><eq></eq></lube><showers><eq></eq></showers><laundry_room><eq></eq></laundry_room><sunoco_fuel><eq></eq></sunoco_fuel></where></formdata></request>'
			yield scrapy.Request(url=init_url + payload, callback=self.body)

	def body(self, response):

		print("=========  Checking.......")
		store_list = response.xpath('//collection//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()')).split('#')[0].strip()
			item['store_number'] = self.validate(store.xpath('.//name/text()')).split('#')[1].strip()
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			item['store_hours'] = self.validate(store.xpath('.//hours/text()'))
			item['store_type'] = self.validate(store.xpath('.//store_type/text()'))
			item['other_fields'] = ''
			item['coming_soon'] = self.validate(store.xpath('.//openingsoon/text()'))
			if item['store_number']+item['address'] in self.history:
				continue
			self.history.append(item['store_number']+item['address'])
			yield item				

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''
