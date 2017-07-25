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

class underarmour(scrapy.Spider):
	name = 'underarmour'
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
		init_url = 'https://hosted.where2getit.com/underarmour/2015/ajax?lang=en-EN&xml_request='
		header = {
			"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
			"Accept-Encoding":"gzip, deflate, br",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.US_location_list:
			payload = '<request><appkey>24358678-428E-11E4-8BC2-2736C403F339</appkey><formdata id="locatorsearch"><countryonly><limit>50</limit><order>name</order></countryonly><dataview>store_default</dataview><order>UASPECIALITY, UAOUTLET, AUTHORIZEDDEALER, rank,_distance</order><limit>25</limit><stateonly>1</stateonly><nobf>1</nobf><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude><country>US</country></geoloc></geolocs><searchradius>25</searchradius><where><or><uaspeciality><eq></eq></uaspeciality><uaoutlet><eq></eq></uaoutlet><authorizeddealer><eq></eq></authorizeddealer></or></where></formdata></request>'
			yield scrapy.Request(url=init_url+payload, headers=header, method='get', callback=self.body)

		for location in self.CA_location_list:
			payload = '<request><appkey>24358678-428E-11E4-8BC2-2736C403F339</appkey><formdata id="locatorsearch"><countryonly><limit>50</limit><order>name</order></countryonly><dataview>store_default</dataview><order>UASPECIALITY, UAOUTLET, AUTHORIZEDDEALER, rank,_distance</order><limit>25</limit><stateonly>1</stateonly><nobf>1</nobf><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude><country>CA</country></geoloc></geolocs><searchradius>25</searchradius><where><or><uaspeciality><eq></eq></uaspeciality><uaoutlet><eq></eq></uaoutlet><authorizeddealer><eq></eq></authorizeddealer></or></where></formdata></request>'
			yield scrapy.Request(url=init_url+payload, headers=header, method='get', callback=self.body)

		for location in self.ALL_location_list:
			payload = '<request><appkey>24358678-428E-11E4-8BC2-2736C403F339</appkey><formdata id="getlist"><order>city</order><objectname>Locator::Store</objectname><where><country><eq>'+location['cca2']+'</eq></country><or><uaspeciality><eq></eq></uaspeciality><uaoutlet><eq></eq></uaoutlet><authorizeddealer><eq></eq></authorizeddealer></or></where></formdata></request>'
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
						if item['address'] != '':
							yield item
				except:
					pass
		except:
			pass	

	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp