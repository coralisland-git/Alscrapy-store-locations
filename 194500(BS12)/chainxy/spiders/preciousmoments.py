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

class preciousmoments(scrapy.Spider):
	name = 'preciousmoments'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.preciousmoments.com/findaretailer'
		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = '<select>' + response.body.split('onChange=displayzipcode(this.value);>')[1].strip().split('<input type="hidden" value="" id="store_count"> -->')[0].strip()[:-9].strip() + '</select>'
		zipcode_list = etree.HTML(data).xpath('//option//text()')
		for zipcode in zipcode_list[1:]:
			url = 'https://www.preciousmoments.com/findaretailer?state=&country=US&state=&city=&zipcode='+zipcode+'&hideit'
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, sdch, br"
			}
			yield scrapy.Request(url=url, headers=header, callback=self.parse_store) 

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="search-area"]/div')
		for store in store_list[:-2]:
			detail = self.eliminate_space(store.xpath('.//text()').extract())
			try:
				item = ChainItem()
				item['store_name'] = self.validate(detail[0])
				address = ''
				for de in detail[1:-1]:
					address += de + ' '
				item['address'] = ''
				item['city'] = ''
				item['state'] = ''
				addr = usaddress.parse(address[:-2])
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
					item['zip_code'] = self.validate(address[-7:])
				item['phone_number'] = detail[-1]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass	

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'N/A' not in self.validate(item):
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
