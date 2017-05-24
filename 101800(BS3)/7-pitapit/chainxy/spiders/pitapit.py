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


class pitapit(scrapy.Spider):
	name = 'pitapit'
	domain = 'https://pitapit.ca/'
	history = []

	def start_requests(self):
	
		init_url  = 'https://www.unoapp.com/app/source/api/index.php?calltype=jsonp&request=location/widget&callback=jQuery1110016124005288633625_1493639086757&api_id=unoapp-generic-key&data%5Bid%5D=8ef23580c964f3754038036876cf0e18'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.body.split('( {')[1].strip()
		store_list = '{' + store_list[:-1]
		store_list = json.loads(store_list)['data']['locations']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['display_name']
			item['store_number'] = store['id']
			item['address'] = store['address']['line1']
			item['address2'] = store['address']['line2']
			item['city'] = store['address']['city']
			item['state'] = store['address']['state']
			item['zip_code'] = store['address']['zip']
			item['country'] = store['address']['country']
			item['phone_number'] = store['profile']['telephone']
			item['latitude'] = store['address']['latitude']
			item['longitude'] = store['address']['longitude']
			h_temp = ''
			hour_list = store['hours']['days_of_the_week']
			week_list= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
			for cnt in range(1, len(hour_list)):
				hour = hour_list[str(cnt)][0]
				h_temp += week_list[int(hour['day'])] + ' ' + hour['starttime'][:-3] + '-' + hour['endtime'][:-3] + ', '
			item['store_hours'] = h_temp[:-1]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_name']+item['store_number'] in self.history:
				continue
			self.history.append(item['store_name']+item['store_number'])
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''