from __future__ import unicode_literals
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

class pharmachoicecanada(scrapy.Spider):
	name = 'pharmachoicecanada'
	domain = 'http://www.pharmachoice.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.US_CA_States_list:
			if location['country'] == 'CA':
				init_url = 'http://www.pharmachoice.com/pc_locate/ajax/province/'+location['abbreviation']
				header = {
					"Accept":"application/json, text/javascript, */*; q=0.01",
					"Accept-Encoding":"gzip, deflate",
					"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
					"X-Requested-With":"XMLHttpRequest"
				}
				formdata = {
					"pc_locate_x_prov":"",
					"js":"true",
					"ajax_page_state[theme]":"pharmachoice",
				}
				yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		data = json.loads(response.body)
		data = data[1]['data'].replace('\u003C','<').replace('\u0022','"').replace('\u003E','>').strip()
		tree = etree.HTML(data)
		store_list = tree.xpath('//a[@class="pc_locate-lnk_set use-ajax"]/@href')
		for store in store_list:
			store = self.domain + store
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = response.xpath('//div[@class="li-overlay l-container-fluid"]//div[@class="li-group"][1]')
			item = ChainItem()
			item['store_name'] = detail.xpath('.//strong/text()').extract_first()
			if item['store_name'] == None:
				item['store_name'] = detail.xpath('.//span[@class="organisation-name"]/text()').extract_first()
			item['address'] = detail.xpath('.//div[@class="thoroughfare"]/text()').extract_first()
			item['city'] = detail.xpath('.//span[@class="locality"]/text()').extract_first()
			item['state'] = detail.xpath('.//span[@class="state"]/text()').extract_first()
			item['zip_code'] = detail.xpath('.//span[@class="postal-code"]/text()').extract_first()
			item['country'] = 'Canada'
			item['phone_number'] = self.eliminate_space(response.xpath('//div[@class="li-overlay l-container-fluid"]//div[@class="li-group"][2]/text()').extract())[0]
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
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''
