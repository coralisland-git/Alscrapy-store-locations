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
import unicodedata

class cookout(scrapy.Spider):
	name = 'cookout'
	domain = ''
	history = []

	def start_requests(self):
			
		init_url = 'http://www.cookout.com/wp-admin/admin-ajax.php?action=store_search&max_results=500&radius=500&autoload=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['store']).replace('&#8211','')
			item['store_number'] = self.validate(store['id'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			h_temp = ''
			hour_list = etree.HTML(store['hours']).xpath('//table//tr')
			for hour in hour_list:
				try:
					h_temp += hour.xpath('.//td[1]/text()')[0] + ' ' + hour.xpath('.//td[2]//text()')[0] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:

			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(';', ',')
		except:
			return ''