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

class lightingone(scrapy.Spider):
	name = 'lightingone'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_US = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list_CA = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.lighting-one.com/wp-admin/admin-ajax.php'
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}

		for location in self.location_list_US:
			formdata = {
				"action":"uxi_locations_finder_data",
				"address": location['city'],
				"radius":"30",
				"id_number":"2",
				"preview_mode":""
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)		

		for location in self.location_list_CA:
			formdata = {
				"action":"uxi_locations_finder_data",
				"address": location['city'],
				"radius":"30",
				"id_number":"2",
				"preview_mode":""
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)		


	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['locations']
		for store in store_list:
			try:
				item = ChainItem()
				item['latitude'] = self.validate(str(store['lat_lng']['lat']))
				item['longitude'] = self.validate(str(store['lat_lng']['lng']))
				store = etree.HTML(store['info_html'])
				detail = self.eliminate_space(store.xpath('.//text()'))
				address = ''
				item['store_name'] = self.validate(detail[0])
				for de in detail[1:]:
					if 'miles' in de.lower():
						break
					address += de + ', '
				item['address'] = ''
				item['city'] = ''
				item['state'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','').upper()
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['state'] = self.validate(item['state'])
				item['country'] = self.check_country(item['state'])
				if item['country'] == 'Canada':
					address = self.eliminate_space(address.split(','))
					if len(address) == 4:
						item['address'] = address[0]
						item['city'] = address[1]
						item['state'] = address[2]
						item['zip_code'] = address[3]
					else:
						item['address'] = address[1]+ address[0]
						item['city'] = address[2]
						item['state'] = address[3]
						item['zip_code'] = address[4]
				if item['address'] not in self.history:
					self.history.append(item['address'])
					yield item		
			except:
				pass

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace(';','').replace('\u2013', '').replace('\\u2019',"'").strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != ',':
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item.upper() in state['abbreviation']:
					return 'United States'
			return 'Canada'