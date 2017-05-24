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

class gretchenscott(scrapy.Spider):
	name = 'gretchenscottme'
	domain = 'https://www.gretchenscottdesigns.com/'
	history = []
	flag_end = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://app.xtremelocator.com/visitor/findLocations.php?sid=1213&zip=20010'
		request = scrapy.Request(url=init_url, callback=self.body)
		request.meta['search_zip'] = '20010'
		yield request

	def body(self, response):
		i = 0
		search_zip = response.meta['search_zip']
		self.flag_end[search_zip] = 0
		while self.flag_end[search_zip] == 0:
			request_url = 'http://app.xtremelocator.com/visitor/results.php?pos=' + str(i)
			request = scrapy.Request(url=request_url, callback=parse_store)
			request.meta['search_zip'] = search_zip
			yield request
			i += 3

	def parse_store(self, response):
		stores = tree.xpath('//li//div[@class="text"]//table//tbody')
		if stores:
			for store in stores:
				info_list = store.xpath('.//tr')
				store_name = info_list[0].xpath('.//td')[1].xpath('./a/text()')[0].strip()
				item = ChainItem()
				item['store_name'] = store_name
				temp_list = info_list[1].xpath('.//td')[1].xpath('./text()')
				temp_address = ''
				for temp in temp_list:
					temp_address += temp.strip() + ' '
				addr = usaddress.parse(temp_address)
				item['city'] = ''
				item['address'] = ''
				for temp in addr:
					if temp[1] == 'PlaceName':
						item['city'] += temp[0].replace(',','')	+ ' '
					elif temp[1] == 'StateName':
						item['state'] = temp[0].replace(',','')
					elif temp[1] == 'ZipCode':
						item['zip_code'] = temp[0].replace(',','')
					else:
						item['address'] += temp[0].replace(',','') + ' '
				if not item['address'].strip() in self.history:
					self.history.append(item['address'].strip())
					item['country'] = info_list[2].xpath('.//td')[1].xpath('./text()')[0].strip()
					yield item
		else:
			search_zip = response.meta['search_zip']
			self.flag_end[search_zip] = 1
			print('============================== end pagination')


	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''