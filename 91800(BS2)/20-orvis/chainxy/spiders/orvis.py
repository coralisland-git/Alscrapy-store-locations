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

class orvis(scrapy.Spider):
	name = 'orvis'
	domain = 'https://www.orvis.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		payload = '<request><appkey>220ADCC1-5B90-3474-BFB1-1062E491086A</appkey><formdata id="getlist"><objectname>Account::Country</objectname><where><name><ne>US</ne></name></where></formdata></request>'
		init_url  = 'http://hosted.where2getit.com/orvis/ajax?&xml_request= %s' % payload
		yield scrapy.Request(url=init_url, callback=self.parse_country) 	

	def parse_country(self, response):
		print("=========  Checking.......")
		country_list = []
		temp_list = response.xpath('//collection//account_country')
		for temp in temp_list:
			name = self.validate(temp.xpath('.//name/text()'))
			country_list.append(name)
		country_list.append('US')
		for country in country_list:
			payload = '<request><appkey>220ADCC1-5B90-3474-BFB1-1062E491086A</appkey><geoip>1</geoip><formdata id="getlist"><order>city</order><objectname>StoreLocator</objectname><where><uid><eq></eq></uid><country><eq>%s</eq></country><or><retailstore><eq>X</eq></retailstore><outletstore><eq>X</eq></outletstore><orvisauthorizedflyfishingdealers><eq>X</eq></orvisauthorizedflyfishingdealers></or></where></formdata></request>' % country
			url  = 'http://hosted.where2getit.com/orvis/ajax?&xml_request= %s' % payload
			yield scrapy.Request(url=url, callback=self.body) 	

	def body(self, response):
		store_list = response.xpath('//collection//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['store_number'] = self.validate(store.xpath('.//uid/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			item['store_hours'] = self.validate(store.xpath('.//hours1/text()'))
			item['store_hours'] += ' ' + self.validate(store.xpath('.//hours2/text()'))
			item['store_hours'] += ' ' + self.validate(store.xpath('.//hours3/text()'))
			item['store_hours'] += ' ' + self.validate(store.xpath('.//hours4/text()'))
			item['store_hours'] += ' ' + self.validate(store.xpath('.//specialhours/text()'))
			item['store_type'] = self.validate(store.xpath('.//type05/text()'))
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace(';','')
		except:
			return ''