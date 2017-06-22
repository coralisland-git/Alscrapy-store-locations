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

class izod(scrapy.Spider):
	name = 'izod'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://secure.gotwww.com/gotlocations.com/vanheusen.new/izod.php'
			header = {
				"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/x-www-form-urlencoded"
			}
			formdata = {
				"Submit.x":"0",
				"Submit.y":"0",
				"address": location['city']
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		try:
			store_list = response.xpath('//div[@id="Layer2"]//table//td')
			for store in store_list:
				try:
					item = ChainItem()
					detail = self.eliminate_space(store.xpath('.//text()').extract())
					item['store_name'] = detail[0].split(':')[1].strip()
					address = detail[1] + ', ' + detail[3]
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
					item['phone_number'] = detail[4].split(':')[1].strip()
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pdb.set_trace()		
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
			if self.validate(item) != '' and 'direction' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp