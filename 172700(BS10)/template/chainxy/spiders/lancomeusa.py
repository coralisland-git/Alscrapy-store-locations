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

class lancomeusa(scrapy.Spider):
	name = 'lancomeusa'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			payload = '<request><appkey>86A84184-140D-11DE-810D-EA9E3B999D57</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude></geoloc></geolocs><searchradius>500</searchradius><where><icon><eq></eq></icon><eventflag1><eq></eq></eventflag1></where></formdata></request>'
			init_url = 'http://hosted.where2getit.com/lancome/ajax?&xml_request=%s' %payload
			yield scrapy.Request(url=init_url,callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()').extract_first())
			uid = self.validate(store.xpath('.//uid/text()').extract_first())
			item['address'] = self.validate(store.xpath('.//address1/text()').extract_first())
			item['address2'] = self.validate(store.xpath('.//address2/text()').extract_first())
			item['city'] = self.validate(store.xpath('.//city/text()').extract_first())
			item['state'] = self.validate(store.xpath('.//state/text()').extract_first())
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()').extract_first())
			item['country'] = self.validate(store.xpath('.//country/text()').extract_first())
			item['phone_number'] = self.validate(store.xpath('.//phone/text()').extract_first())
			item['latitude'] = self.validate(store.xpath('.//latitude/text()').extract_first())
			item['longitude'] = self.validate(store.xpath('.//longitude/text()').extract_first())
			if item['store_name'] + item['phone_number'] not in self.history:
				self.history.append(item['store_name'] + item['phone_number'])
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
