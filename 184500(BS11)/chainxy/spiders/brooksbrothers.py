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

class brooksbrothers(scrapy.Spider):
	name = 'brooksbrothers'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
			"Accept-Encoding":"gzip, deflate, sdch",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			payload = '<request><appkey>AF20A24E-B672-11DD-A6BC-0AC524FB2E6B</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>'+location['abbreviation']+'</addressline><latitude></latitude><longitude></longitude><country></country></geoloc></geolocs><searchradius>15|25|50|100|250</searchradius><criteria><field>productlist</field><fieldvalue>X</fieldvalue><fieldop>eq</fieldop></criteria><where><productlist><eq></eq></productlist></where><stateonly>1</stateonly></formdata></request>'
			init_url = 'http://mobile.where2getit.com/brooksbrothers/ajax?&xml_request=%s' %payload
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//poi')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//name/text()'))
				check = self.validate(store.xpath('.//uid/text()'))
				item['address'] = self.validate(store.xpath('.//address1/text()'))
				item['address2'] = self.validate(store.xpath('.//address2/text()'))
				item['city'] = self.validate(store.xpath('.//city/text()'))
				item['state'] = self.validate(store.xpath('.//state/text()'))
				if item['state'] == '':
					item['state'] = self.validate(store.xpath('.//province/text()'))
				item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
				item['country'] = self.validate(store.xpath('.//country/text()'))
				item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
				item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
				item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
				item['store_hours'] = self.validate(store.xpath('.//hours/text()')).replace('<br>',', ').replace('TO', '-')
				if check not in self.history:
					self.history.append(check)
					yield item	
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
