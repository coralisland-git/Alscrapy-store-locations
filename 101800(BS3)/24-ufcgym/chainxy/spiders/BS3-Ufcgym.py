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

class BS3Ufcgym(scrapy.Spider):
	name = 'BS3-Ufcgym'
	domain = 'https://www.ufcgym.com/'
	history = []

	def start_requests(self):
		init_url = 'https://ufcgym.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = response.xpath('//script[@charset="utf-8"]').extract_first()
		data = data.split('locations = ')[1].split('</script>')[0].strip()[:-1]
		store_list = json.loads(data)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = ''
			item['address'] = store['street_address']
			item['address2'] = ''
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['postal_code']
			if len(item['zip_code']) > 5:
				item['country'] = 'Canada'
			else:
				item['country'] = 'United States'
			item['phone_number'] = store['phone']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			item['store_hours'] = 'Mon' + ' ' + store['hours_mon'] + ', '
			item['store_hours'] += 'Tue' + ' ' + store['hours_tue'] + ', '
			item['store_hours'] += 'Wed' + ' ' + store['hours_wed'] + ', '
			item['store_hours'] += 'Thu' + ' ' + store['hours_thu'] + ', '
			item['store_hours'] += 'Fri' + ' ' + store['hours_fri'] + ', '
			item['store_hours'] += 'Sat' + ' ' + store['hours_sat'] + ', '
			item['store_hours'] += 'Sun' + ' ' + store['hours_sun']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''