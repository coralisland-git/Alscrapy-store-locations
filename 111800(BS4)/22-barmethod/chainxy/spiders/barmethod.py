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
import pdb

class barmethod(scrapy.Spider):
	name = 'barmethod'
	domain = 'http://barmethod.com/'
	history = []


	def start_requests(self):
		
		init_url = 'http://barmethod.com/locations/view-all-locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		extra = response.xpath('//div[contains(@class, "toggle_content")]/p')
		for ex in extra:
			temp = ex.xpath('.//text()').extract()
			if len(temp) != 0:
				yield self.parse_store(temp)

		store_list = response.xpath('//div[contains(@class, "content-column")]')
		for store in store_list:
			try :
				temp = store.xpath('./text()').extract()
				dump = []
				for t in temp:
					if t.strip() != '':
						dump.append(t)

				if len(dump) != 0:
					if self.contain_check(dump):
						if len(dump) == 4:
							item = ChainItem()
							item['store_name'] = self.validate(store.xpath('./a/text()').extract_first())
							item['address'] = self.validate(dump[2])
							address = dump[3].split(',')
							item['city'] = self.validate(address[0])
							item['state'] = self.validate(address[1].strip().split(' ')[0])
							item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
							yield item
						else :
							item = ChainItem()
							item['store_name'] = self.validate(store.xpath('./a/text()').extract_first())
							if item['store_name'] == '':
								item['store_name'] = self.validate(store.xpath('./text()').extract_first())

						item['country'] = 'United States'
						item['coming_soon'] = '1'
						yield item

					else:
						item = ChainItem()
						item['store_name'] = self.validate(store.xpath('./a/text()').extract_first())

						if len(dump) == 4:
							item['address'] = self.validate(dump[1])
							address = dump[2].split(',')
							item['city'] = self.validate(address[0])
							item['state'] = self.validate(address[1].strip().split(' ')[0])
							item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
							item['phone_number'] = self.validate(dump[3])
						elif len(dump) == 3:
							item['address'] = self.validate(dump[0])
							address = dump[1].split(',')
							item['city'] = self.validate(address[0])
							item['state'] = self.validate(address[1].strip().split(' ')[0])
							item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
							item['phone_number'] = self.validate(dump[2])
						elif len(dump) == 2:
							item['address'] = self.validate(dump[0])
							address = dump[1].split(',')
							item['city'] = self.validate(address[0])
							item['state'] = self.validate(address[1].strip().split(' ')[0])
							item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
						
						try:
							zip_temp = int(item['zip_code'])
							item['country'] = 'United States'
						except:
							item['country'] = 'Canada'

						item['coming_soon'] = '0'
						yield item
			except:
				pass

			data = store.xpath('.//p//text()').extract()
			if len(data) != 0:
				for p_store in store.xpath('.//p'):
					temp = p_store.xpath('.//text()').extract()
					yield self.parse_store(temp)

	def parse_store(self, temp):
		try :
			item = ChainItem()
			if self.contain_check(temp):
				if len(temp) == 4:
					item['store_name'] = self.validate(temp[0])
					item['address'] = self.validate(temp[2])
					address = temp[3].split(',')
					item['city'] = self.validate(address[0])
					item['state'] = self.validate(address[1].strip().split(' ')[0])
					item['zip_code'] = self.validate(address[1].strip().split(' ')[1])

				else :
					item['store_name'] = self.validate(temp[0])

				item['country'] = 'United States'
				item['coming_soon'] = '1'

				return item

			else:
				if len(temp) == 4:
					item['store_name'] = self.validate(temp[0])
					item['address'] = self.validate(temp[1])
					address = temp[2].split(',')
					item['city'] = self.validate(address[0])
					item['state'] = self.validate(address[1].strip().split(' ')[0])
					item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
					item['phone_number'] = self.validate(temp[3])
					
				elif len(temp) == 5:
					item['store_name'] = self.validate(temp[0])
					item['address'] = self.validate(temp[2])
					address = temp[3].split(',')
					item['city'] = self.validate(address[0])
					item['state'] = self.validate(address[1].strip().split(' ')[0])
					item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
					item['phone_number'] = self.validate(temp[4])
				
				elif len(temp) == 3 :
					item['store_name'] = self.validate(temp[0])
					item['address'] = self.validate(temp[1])
					address = temp[2].split(',')
					item['city'] = self.validate(address[0])
					item['state'] = self.validate(address[1].strip().split(' ')[0])
					item['zip_code'] = self.validate(address[1].strip().split(' ')[1])
					
				else :
					pass
				try:
					zip_temp = int(item['zip_code'])
					item['country'] = 'United States'
				except:
					item['country'] = 'Canada'
				item['coming_soon'] = '0'

				return item
		except:
			return None

	def contain_check(self, item_list):
		cnt = 0
		for item in item_list:
			if 'Opening' in item.strip() or 'Coming' in item.strip():
				cnt += 1
		if cnt == 0:
			return False
		else:
			return True

	def validate(self, item):
		try:
			item = unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
			if '>' in item:
				item = item.replace('>', ' ')
			return item.strip() 
		except:
			return ''