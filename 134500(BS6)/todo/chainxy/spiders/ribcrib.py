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
import unicodedata

class Ribcrib(scrapy.Spider):
	name = 'ribcrib'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.ribcrib.com/wp-admin/admin-ajax.php'
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest'
		}
		for location in self.location_list:
			formdata={
				'action':'locate',
				'address':location['city'],
				'formatted_address':'%s, %s, USA' %(location['city'], location['state']),
				'locatorNonce':'827066cecd',
				'distance':'100',
				'latitude':str(location['latitude']),
				'longitude':str(location['longitude']),
				'unit':'miles',
				'geolocation':'false',
				'allow_empty_address':'false'
			}
			yield scrapy.FormRequest(url=init_url, method='post', headers=header, formdata=formdata, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['results']
			for store in store_list:
				item = ChainItem()
				detail_url = etree.HTML(store['output']).xpath('//a/@href')[0]
				request = scrapy.Request(url=detail_url, callback=self.parse_page)
				request.meta['store_name'] = self.validate(store['title'])
				request.meta['latitude'] = self.validate(store['latitude'])
				request.meta['longitude'] = self.validate(store['longitude'])
				yield request
		except:
			pass

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = response.meta['store_name']
		item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())	
		item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())	
		item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())	
		item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())	
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//a[@itemprop="telephone"]/text()').extract_first())	
		item['latitude'] = response.meta['latitude']
		item['longitude'] = response.meta['longitude']
		h_temp = ''
		hour_list = response.xpath('//div[@class="location_info__hours"]/text()').extract()
		for hour in hour_list:
			if self.validate(hour) != '':
				h_temp += self.validate(hour) + ', '
		item['store_hours'] = h_temp[:-2]		
		if item['address']+item['phone_number'] not in self.history:
			self.history.append(item['address']+item['phone_number'])
			yield item		

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace('\t', '').replace('\n', '').replace('  ', '')
		except:
			return ''