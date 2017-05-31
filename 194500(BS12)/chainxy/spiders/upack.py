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

class upack(scrapy.Spider):
	name = 'upack'
	domain = 'http://www.upack.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.pods.com/locations/location-search'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="locations-list"]')
		header = {
			"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"accept-encoding":"gzip, deflate, sdch, br"
		}
		for store in store_list:
			country = self.validate(store.xpath('.//h3/text()').extract_first()).lower()
			if 'kingdom' not in country or 'australia' not in country:
				store = store.xpath('.//a/@href').extract()
				for store_link in store:
					store_link = self.domain + store_link
					yield scrapy.Request(url=store_link, headers=header, callback=self.parse_page)
					
	def parse_page(self, response):
		try:
			item = ChainItem()
			store_list = response.xpath('//div[@id="main-content"]/div[contains(@class, "row")]//div[contains(@class, "column")]')
			for store in store_list:	
				item['store_name'] = self.validate(response.url.split('/')[-1])
				addr_list = self.eliminate_space(store.xpath('.//text()').extract())
				address = ''
				for addr in addr_list:
					address += addr + ' '
				item['address'] = ''
				item['city'] = ''
				addr = usaddress.parse(address)
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',', '') + ' '
				item['country'] = self.check_country(item['state'])
				if item['country'] == 'Canada':
					item['address'] = addr_list[0]
					item['city'] = self.validate(addr_list[1].split(',')[0])
					item['state'] = self.validate(addr_list[1].split(',')[1])[:2].strip()
					item['zip_code'] = self.validate(addr_list[1].split(',')[0])[2:].strip()					
				yield item
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('  ','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'