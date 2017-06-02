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
import pdb

class napaonline(scrapy.Spider):
	name = 'napaonline'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.napaonline.com/en/store-finder?q='+location['city']
		# init_url = 'https://www.napaonline.com/en/store-finder?q=new+york'
			header = {
				"Accept":"text/html, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest",
				"X-Distil-Ajax":"vaxycdfb",
				"Cookie":'napa-anonymousUserVisit=""; ROUTEID=.2014; mf_ad06e891-9349-4c4a-9d70-4ed16de161aa=-1; D_SID=64.64.117.119:xpOHf7VVBPHTuy59f0ywLuXGx1FT9DP+YnQ4Erhfnrk; _ga=GA1.2.1657479044.1496330406; _gid=GA1.2.138334180.1496330416; s_cc=true; D_IID=00516B54-26B1-307D-8F47-B4400E8FF20F; D_UID=DF5E9C6C-D906-34E1-B23C-0470A5E35762; D_ZID=D8CEA139-9AB3-3875-BA9B-552767DA749A; D_ZUID=8AD373BA-6C3F-3FBE-9245-1BED0918A305; D_HID=83248417-78BC-3417-88A9-AC36F0630A63; s_sq=%5B%5BB%5D%5D; JSESSIONID=649C4376453AE4161A90C10CACBC368E; s_vi=[CS]v1|2C98185A05079F34-40000108E000049A[CE]; _bcvm_vid_1505075094761579602=578206569774713437T6AB0FC13751EB890A0C603BF91CB7E5F2AF5A5A65290B4914B3ED33AA31CBA5C1C910540C3E7277B60BCAEF4AA484E45338B5626FB41E5470FC1E4EE37602326; _bcvm_vrid_1505075094761579602=578206569796194004T654DCB30802627303A450BCCEA1FCBDFAEC2DD2BBA7D3C50A5D0AE96E6B09F53982705639330D7E386C7485AC3F206AE0ED8BC80CB2B63042D9D9181B5D71B0E; s_fid=664A2B911E17F703-391DBFD1BC976995; s_nr=1496331415833-New; gpv_pn=store-locator'
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="store-listing"]//li')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('//div[@class="title-1"]/text()').extract_first()) + ' ' + self.validate(response.xpath('//div[@class="title-2"]/text()').extract_first())
				address = self.validate(store.xpath('//div[@class="address-1"]/text()').extract_first()) + ' ' + self.str_concat(response.xpath('//div[@class="address-2"]/text()').extract(), ', ')
				item['address'] = ''
				item['city'] = ''
				item['state'] = ''
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
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(store.xpath('//div[@class="phone"]/text()').extract_first())
				h_temp = ''
				hour_list = self.eliminate_space(store.xpath('//div[@class="store-hours"]//text()').extract())
				cnt = 1
				for hour in hour_list:
					h_temp += hour
					if cnt % 2 == 0:
						h_temp += ', '
					else:
						h_temp += ' '
					cnt += 1
				item['store_hours'] = h_temp[:-2]
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pdb.set_trace()		

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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''