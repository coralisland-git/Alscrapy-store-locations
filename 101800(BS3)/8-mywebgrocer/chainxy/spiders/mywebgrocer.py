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

class mywebgrocer(scrapy.Spider):
	name = 'mywebgrocer'
	domain = 'http://acmemarkets.mywebgrocer.com'
	history = []

	def start_requests(self):

		init_url  = 'http://acmemarkets.mywebgrocer.com/Stores'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		
		header = {
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/json',
			'X-Requested-With':'XMLHttpRequest'
		}
		state_list = response.xpath('.//select[@id="StateDropDown"]//option//text()').extract()
		for state in state_list:
			city_url = 'http://acmemarkets.mywebgrocer.com/Ajax/Stores/Cir/Country/United%20States/Region/'+state+'/Cities' 
			request = scrapy.Request(url=city_url, headers=header, method='POST', callback=self.parse_city)
			request.meta['state'] = state
			yield request
		
		# yield scrapy.Request(url='http://acmemarkets.mywebgrocer.com/Ajax/Stores/Cir/Country/United%20States/Region/Connecticut/Cities', headers=header, method='POST', callback=self.parse_city)

	def parse_city(self, response):
		city_list = json.loads(response.body)
		# with open('city.html', 'wb') as f:
		# 	f.write(response.body)
		for city in city_list:
			store_url = 'http://acmemarkets.mywebgrocer.com/Stores/Get?Country=United%20States&Region='+response.meta['state']+'&City=' + city['Name']
			print('store ===================  ', store_url )
			yield scrapy.Request(url=store_url, callback=self.parse_store)
		# init_url = 'http://acmemarkets.mywebgrocer.com/Stores/Get?Country=United%20States&Region=New%20York&City=Brewster&Radius=20&Units=Miles&StoreType=Cir&StoresPageSize=undefined&IsShortList=undefined&_=1493603985634'
		# init_url = 'http://acmemarkets.mywebgrocer.com/Stores/Get?Country=United%20States&Region=New York&City=Brewster'
		# yield scrapy.Request(url="http://acmemarkets.mywebgrocer.com/Stores/Get?Country=United%20States&Region=Delaware&City=Dover", callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//div[@class="store-item store-item-none"]')
		try:
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[@class="storelist-info-text"]//h4/text()'))
				item['store_number'] = ''
				item['address'] = self.validate(store.xpath('.//div[@class="storelist-info-text"]//p[1]/text()'))
				item['address2'] = ''
				address = self.validate(store.xpath('.//div[@class="storelist-info-text"]//p[2]/text()'))
				item['city'] = address.split(',')[0].strip()
				temp = address.split(',')[1].strip().split(' ')
				c_temp = ''
				for cnt in range(0, len(temp)-1):
					c_temp += temp[cnt].strip() + ' '
				item['state'] = c_temp
				item['zip_code'] = temp[len(temp)-1]
				item['country'] = 'United States'
				try:
					item['phone_number'] = self.validate(store.xpath('.//div[@class="storelist-info-text"]//p[@class="storelist-phone-directions"]//span/text()')).split(':')[1].strip()
				except:
					item['phone_number'] = ''
				item['latitude'] = ''
				item['longitude'] = ''
				h_temp = ''
				hour_list = store.xpath('.//div[@id="StoreServicesContainer"]//span/text()').extract()
				for hour in hour_list:
					h_temp += hour.strip() + ', '
				item['store_hours'] = h_temp[:-2]
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['store_name'] + item['phone_number'] in self.history:
					continue
				self.history.append(item['store_name'] + item['phone_number'])
				yield item
		except:
			pdb.set_trace()			

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''