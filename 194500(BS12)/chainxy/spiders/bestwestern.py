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
import geocoder
import pdb

class bestwestern(scrapy.Spider):
	name = 'bestwestern'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		# init_url = 'https://www.bestwestern.com/en_US.html'
		# yield scrapy.Request(url=init_url, callback=self.body) 
		header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest"
			}
		yield scrapy.Request(url='https://www.bestwestern.com/bin/bestwestern/proxy?gwServiceURL=HOTEL_SEARCH&distance=50&depth=2&checkinDate=2017-05-30&checkoutDate=2017-05-31&latitude=33.8365932&longitude=-117.91430120000001&numberOfRooms=1&occupant=numAdults:1,numChild:0', headers=header, method='get', callback=self.parse_store)

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		state_list = response.xpath('//div[@class="itemContent"]//div[@class="richTextEditorExtended parbase"]//a/text()').extract()
		for state in state_list:
			state = state.split(',')[0] + ', ' + self.validate(state.split(',')[1]).split(' ')[0]
			location = geocoder.google(state)
			pdb.set_trace()
			header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest"
			}
			url = 'https://www.bestwestern.com/bin/bestwestern/proxy?gwServiceURL=HOTEL_SEARCH&distance=50&depth=2&checkinDate=2017-05-30&checkoutDate=2017-05-31&latitude='+str(location.latlng[0])+'&longitude='+str(location.latlng[1])+'&numberOfRooms=1&occupant=numAdults:1,numChild:0'
			location.latlng[0]
			location.latlng[1]

	def parse_store(self, response):
		print('~~~~~~~~~~~~~~~~~~')
			# try:
			# 	item = ChainItem()
			# 	detail = self.eliminate_space(store.xpath())
			# 	item['store_name'] = self.validate(store['name'])
			# 	item['store_number'] = self.validate(store['store_number'])
			# 	item['address'] = self.validate(store['address'])
			# 	item['address2'] = self.validate(store['address2'])
				
			# 	address = ''
			# 	item['address'] = ''
			# 	item['city'] = ''
			# 	addr = usaddress.parse(address)
			# 	for temp in addr:
			# 		if temp[1] == 'PlaceName':
			# 			item['city'] += temp[0].replace(',','')	+ ' '
			# 		elif temp[1] == 'StateName':
			# 			item['state'] = temp[0].replace(',','')
			# 		elif temp[1] == 'ZipCode':
			# 			item['zip_code'] = temp[0].replace(',','')
			# 		else:
			# 			item['address'] += temp[0].replace(',', '') + ' '

			# 	address = ''
			# 	addr = address.split(',')
			# 	item['city'] = self.validate(addr[0].strip())
			# 	item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			# 	item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

			# 	item['city'] = self.validate(store['city'])
			# 	item['state'] = self.validate(store['state'])
			# 	item['zip_code'] = self.validate(store['zip'])
			# 	item['country'] = self.validate(store['country'])
			# 	item['phone_number'] = self.validate(store['phone'])
			# 	item['latitude'] = self.validate(store['latitude'])
			# 	item['longitude'] = self.validate(store['longitude'])

			# 	h_temp = ''
			# 	hour_list = self.eliminate_space(response.xpath('//text()').extract())
			# 	cnt = 1
			# 	for hour in hour_list:
			# 		h_temp += hour
			# 		if cnt % 2 == 0:
			# 			h_temp += ', '
			# 		else:
			# 			h_temp += ' '
			# 		cnt += 1
			# 	item['store_hours'] = h_temp[:-2]

			# 	item['store_hours'] = self.validate(store['hours'])
			# 	item['store_type'] = ''
			# 	item['other_fields'] = ''
			# 	item['coming_soon'] = ''
			# 	if item['store_number'] not in self.history:
			# 		self.history.append(item['store_number'])
			# 		yield item	
			# except:
			# 	pdb.set_trace()		

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