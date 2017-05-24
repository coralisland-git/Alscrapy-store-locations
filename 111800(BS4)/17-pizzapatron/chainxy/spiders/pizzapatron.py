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

class pizzapatron(scrapy.Spider):
	name = 'pizzapatron'
	domain = 'http://pizzapatron.com'
	history = []

	def start_requests(self):
		
		init_url = 'http://pizzapatron.com/wp-admin/admin-ajax.php'
		formdata = {
				'action':'store_wpress_listener',
				'method':'display_list',
				'lat':'',
				'lng':'',
				'category_id':'',
				'radius_id':'',
				'nb_display':'200',
				'display_type':'undefined'
			}
		yield scrapy.FormRequest(url=init_url, formdata=formdata, method="POST", callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = json.loads(response.body)['stores']
		store_list = etree.HTML(data).xpath('//div[contains(@style, "padding-bottom:10px; border-bottom: 1px solid #e7e7e7; overflow:hidden;")]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = 'Pizza Patron'
				item['store_number'] = ''
				item['address'] = self.validate(store.xpath('.//div[@class="c4"][1]/text()')[0])
				item['address2'] = ''
				try:
					address = store.xpath('.//div[@class="c4"][1]/text()')[1].split(',')
					item['city'] = self.validate(address[0])
					try:
						item['state'] = self.validate(address[1]).split(' ')[0]
						item['zip_code'] = self.validate(address[1]).split(' ')[1]
					except:
						item['state'] = self.validate(address[1])
				except:
					pass
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//div[@class="c4"][1]//a/text()')[0])
				h_temp = ''
				hour_list = store.xpath('.//div[@class="c4"][2]/text()')
				for hour in hour_list:
					h_temp += hour + '. '
				item['store_hours'] = h_temp[:-2]
				yield item		
			except:
				pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''