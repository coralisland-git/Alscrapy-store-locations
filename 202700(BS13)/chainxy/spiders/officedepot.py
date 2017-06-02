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

class officedepot(scrapy.Spider):
	name = 'officedepot'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
			"Accept-Encoding":"gzip, deflate, sdch"
		}
		for location in self.location_list:
		  	payload = '<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>20|35|50|100|250</searchradius><where><or><nowdocs><eq></eq></nowdocs><expanded_furn><eq></eq></expanded_furn><usps><eq></eq></usps><shredding><eq></eq></shredding><selfservews><eq></eq></selfservews><photoprint><eq></eq></photoprint><expandedbb><eq></eq></expandedbb><listeningstation><eq></eq></listeningstation><cellphonerepair><in></in></cellphonerepair><techtradein><eq></eq></techtradein><techrecycling><eq></eq></techrecycling></or><icon><eq></eq></icon></where></formdata></request>'
			init_url = 'http://storelocator.officedepot.com/ajax?&xml_request=%s' %payload
			yield scrapy.Request(url=init_url,headers=header, callback=self.body) 

	def body(self, response):
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
			week_list = ['mon', 'tues', 'wed', 'thur', 'fri', 'sat', 'sun']
			h_temp = ''
			for week in week_list:
				try:
					h_temp += week.upper() + ' ' + self.validate(store.xpath('.//'+week+'/text()').extract_first()) + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
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
