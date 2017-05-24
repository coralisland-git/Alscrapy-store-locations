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

class buckle(scrapy.Spider):
	name = 'buckle'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			header = {
				"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest"
			}
			payload = '<request><appkey>6EE99756-D695-11DD-9784-7F4437ABAA09</appkey><geoip>1</geoip><formdata id="getlist"><objectname>StoreLocator</objectname><where><uid><eq></eq></uid><state><eq>'+location['abbreviation']+'</eq></state><store><in></in></store></where></formdata></request>'
			init_url = 'https://hosted.where2getit.com/buckle/ajax?&xml_request=%s' %payload
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//poi')
		for store in store_list:
			try:
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
				week_list = ['mon', 'tue','wed', 'thu','fri', 'sat', 'sun']
				h_temp = ''
				for week in week_list:
					h_temp += week.upper() + ' ' + self.validate(store.xpath('.//'+week+'open/text()')) + '-' + self.validate(store.xpath('.//'+week+'close/text()')) +', '
				item['store_hours'] = h_temp[:-2]
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					yield item	
			except:
				pass


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