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
import pdb

class tonyromas(scrapy.Spider):
	name = 'tonyromas'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://tonyromas.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//div[@class="col col1"]//a/text()').extract()
		store_list.append('Guam')
		url = 'https://tonyromas.com/wp-admin/admin-ajax.php'
		header = {
			'accept':'*/*',
			'accept-encoding':'gzip, deflate, br',
			'content-type':'application/x-www-form-urlencoded; charset=UTF-8'
		}
		for store in store_list:
			formdata = {
				'the_location':store,
				'search_distance':'100',
				'current_lat':'',
				'current_lng':'',
				'current_page':'1',
				'action':'locationsubmit'
			}
			yield scrapy.FormRequest(url=url, method='post', headers=header, formdata=formdata, callback=self.parse_page)

	def parse_page(self, response):
		data = json.loads(response.body)['newresults2']
		store_list = etree.HTML(data).xpath('//div[@class="a-result"]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.format(store.xpath('.//div[@class="title"]/text()')[0])			
			address = self.validate(store.xpath('.//div[@class="address"]/text()')[0])
			item['address'] = ''
			item['city'] = ''
			item['state'] = ''
			addr = usaddress.parse(address)
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0]
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '

			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]/text()')[0])
			h_temp = ''
			hour_list = self.eliminate_space(store.xpath('.//div[@class="the-hours"]/text()'))
			for hour in hour_list:
				h_temp += self.validate(hour) + ', '
			item['store_hours'] = h_temp[:-2]
			if item['store_hours'] == '':
				item['country'] = 'Guam'
				item['address'] = item['address'].replace('Guam','')
			yield item			


	def validate(self, item):
		try:
			return item.strip().replace('\r',' ').replace('\n',' ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '').strip()
		except:
			return ''