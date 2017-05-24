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
import math
import unicodedata

class burgerkingcanada(scrapy.Spider):
	name = 'burgerkingcanada'
	domain = 'http://burgerking.ca'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://burgerking.ca/locations?field_geofield_distance[origin][lat]='+str(location['latitude'])+'&field_geofield_distance[origin][lon]='+str(location['longitude'])
			yield scrapy.Request(url=init_url, callback=self.body, meta={'country':location['city']}) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			count =  self.validate(response.xpath('//div[@class="bk-restaurants-total"]/text()'))
			count = int(math.ceil(int(count)/4.0))
			for cnt in range(0, count):
				url_template = response.url + '&page=' + str(cnt) + '&target=' + response.meta['country']
				yield scrapy.Request(url=url_template, callback=self.parse_page)
		except:
			if count != '':
				pdb.set_trace()
			else :
				pass

	def parse_page(self, response):
		with open('burger.html' ,'wb') as f:
			f.write(response.body)
		store_list = response.xpath('//div[@class="bk-restaurants"]//ul//li')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//div[@class="bk-location-title"]/text()'))
			item['store_number'] = self.validate(store.xpath('.//div[@class="bk-id"]/text()'))
			item['address'] = self.validate(store.xpath('.//div[@class="bk-address1"]/text()'))
			item['city'] = self.validate(store.xpath('.//div[@class="bk-city"]/text()'))
			item['state'] = self.validate(store.xpath('.//div[@class="bk-state"]/text()'))
			item['zip_code'] = self.validate(store.xpath('.//div[@class="bk-zip"]/text()'))
			item['country'] = self.validate(store.xpath('.//div[@class="bk-country"]/text()'))
			item['phone_number'] = self.validate(store.xpath('.//div[@class="bk-phone"]/text()'))
			item['latitude'] = self.validate(store.xpath('.//div[@class="bk-latitude"]/text()'))
			item['longitude'] = self.validate(store.xpath('.//div[@class="bk-longitude"]/text()'))
			h_temp = ''
			week_list = ['mon','tue', 'wed', 'thu','fri', 'sat', 'sun']
			for week in week_list:
				try:
					time = self.validate(store.xpath('.//div[@class="bk-location_'+week+'_dining"]/text()')).split(';')
					h_temp += week + ' ' + time[0].split(' ')[1][:-3] + ' - ' + time[1].split(' ')[1][:-3] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item	

	def validate(self, item):
		try:
			item = item.extract_first().strip()
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''