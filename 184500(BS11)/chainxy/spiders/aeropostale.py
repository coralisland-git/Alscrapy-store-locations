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

class aeropostale(scrapy.Spider):
	name = 'aeropostale'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.aeropostale.com/storeLocator/results.jsp'

		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded"
		}
		
		for location in self.location_list:
			formdata = {
				"action":"SEARCH_FOR_STORES",
				"postalCode":"",
				"radius":"50",
				"searchType":"STATE",
				"typeId":"",
				"city":"",
				"state":location['abbreviation'],
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		store_list = response.xpath('//table//tr')
		for store in store_list:
			try:
				item = ChainItem()
				address_temp = self.eliminate_space(store.xpath('.//td[2]//text()').extract())			
				item['store_name'] = address_temp[0]
				address = address_temp[1] + ', ' + address_temp[2]
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
				item['country'] = 'United States'
				p_temp = self.eliminate_space(store.xpath('.//td[1]//text()').extract())
				item['phone_number'] = p_temp[1]
				if item['address'] + item['phone_number'] not in self.history:
					self.history.append(item['address'] + item['phone_number'])
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
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp