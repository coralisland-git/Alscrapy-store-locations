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
import usaddress

class timberland(scrapy.Spider):
	name = 'timberland'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_location_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_location_list = json.load(data_file)
		file_path = script_dir + '/geo/All_Countries.json'
		with open(file_path) as data_file:    
			self.ALL_location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://hosted.where2getit.com/timberland/local/ajax?lang=en-EN&xml_request='
		header = {
			"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
			"Accept-Encoding":"gzip, deflate, br",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.US_location_list:
			payload = '<request><appkey>3BD8F794-CA9E-11E5-A9D5-072FD1784D66</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><order>retail_store,_distance</order><limit>5000</limit><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude><country>US</country></geoloc></geolocs><radiusuom></radiusuom><searchradius>10|25|50|75</searchradius><where><or><retail_store><eq></eq></retail_store><factory_outlet><eq></eq></factory_outlet><authorized_reseller><eq></eq></authorized_reseller><icon><eq></eq></icon><pro_workwear><eq></eq></pro_workwear><pro_footwear><eq></eq></pro_footwear></or></where></formdata></request>'
			yield scrapy.Request(url=init_url+payload, headers=header, method='get', callback=self.body)

		for location in self.CA_location_list:
			payload = '<request><appkey>3BD8F794-CA9E-11E5-A9D5-072FD1784D66</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><order>retail_store,_distance</order><limit>5000</limit><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude><country>CA</country></geoloc></geolocs><radiusuom></radiusuom><searchradius>10|25|50|75</searchradius><where><or><retail_store><eq></eq></retail_store><factory_outlet><eq></eq></factory_outlet><authorized_reseller><eq></eq></authorized_reseller><icon><eq></eq></icon><pro_workwear><eq></eq></pro_workwear><pro_footwear><eq></eq></pro_footwear></or></where></formdata></request>'
			yield scrapy.Request(url=init_url+payload, headers=header, method='get', callback=self.body)

		for location in self.ALL_location_list:
			payload = '<request><appkey>3BD8F794-CA9E-11E5-A9D5-072FD1784D66</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><order>retail_store,_distance</order><limit>5000</limit><geolocs><geoloc><addressline>'+location['capital']+'</addressline><longitude>'+str(location['latlng'][1])+'</longitude><latitude>'+str(location['latlng'][0])+'</latitude><country>'+location['cca2']+'</country></geoloc></geolocs><radiusuom></radiusuom><searchradius>10|25|50|75</searchradius><where><or><retail_store><eq></eq></retail_store><factory_outlet><eq></eq></factory_outlet><authorized_reseller><eq></eq></authorized_reseller><icon><eq></eq></icon><pro_workwear><eq></eq></pro_workwear><pro_footwear><eq></eq></pro_footwear></or></where></formdata></request>'	
			yield scrapy.Request(url=init_url+payload, headers=header, method='get', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")	
		try:
			store_list = response.xpath('//response//collection//poi')
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('./name/text()').extract_first())
					item['address'] = self.validate(store.xpath('./address1/text()').extract_first())
					item['address2'] = self.validate(store.xpath('./address2/text()').extract_first())
					item['city'] = self.validate(store.xpath('./city/text()').extract_first())
					item['state'] = self.validate(store.xpath('./province/text()').extract_first())
					if item['state'] == '':
						item['state'] = self.validate(store.xpath('./state/text()').extract_first())
					item['zip_code'] = self.validate(store.xpath('./postalcode/text()').extract_first())
					item['country'] = self.validate(store.xpath('./country/text()').extract_first())
					item['phone_number'] = self.validate(store.xpath('./phone/text()').extract_first())
					item['latitude'] = self.validate(store.xpath('./latitude/text()').extract_first())
					item['longitude'] = self.validate(store.xpath('./longitude/text()').extract_first())
					uid = self.validate(store.xpath('./uid/text()').extract_first())
					if uid not in self.history:
						self.history.append(uid)
						yield item
				except:
					pass
		except:
			pass	

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