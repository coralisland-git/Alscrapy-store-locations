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
import pdb

class benjerrys(scrapy.Spider):
	name = 'benjerrys'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://benjerry.where2getit.com/ajax?lang=en_US&xml_request='
			payload = '<request><appkey>3D71930E-EC80-11E6-A0AE-8347407E493E</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>100</limit><geolocs><geoloc><addressline>'+location['city']+'</addressline><longitude>'+str(location['longitude'])+'</longitude><latitude>'+str(location['latitude'])+'</latitude><country>US</country></geoloc></geolocs><searchradius>500</searchradius><order>RANK, _distance</order><stateonly>1</stateonly><radiusuom></radiusuom><proximitymethod>drivetime</proximitymethod><cutoff>500</cutoff><cutoffuom>mile</cutoffuom><distancefrom>0.01</distancefrom><where><or><cakesforsale><eq></eq></cakesforsale><catering><eq></eq></catering><fcd><eq></eq></fcd><flavorserved><eq></eq></flavorserved></or><icon><distinctfrom></distinctfrom></icon><clientkey><notin>FLL01,FLL02,FLL05,FLL08,FLL09,MDL01,TXL01,NJL06,CAL07,NJL07,FLL12,FLL16,FLL18,FLL19,CA102,FL050,FL051,FL053,FL054,FL055,FL056,FL058,FL061,FL063,FL064,FL065,MD017,NJ030,NJ031,TX029</notin></clientkey></where></formdata></request>'
			url = init_url + payload
			yield scrapy.Request(url=url, callback=self.body) 

	def body(self, response):
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = response.xpath('//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//cakephone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
			h_temp = ''
			for week in week_list:
				h_temp += week + ' ' + self.validate(store.xpath('.//'+week+'/text()')) +', '
			item['store_hours'] = h_temp[:-2]
			uid = self.validate(store.xpath('.//uid/text()'))
			if uid not in self.history:
				self.history.append(uid)
				yield item		

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''