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

class lego(scrapy.Spider):
	name = 'lego'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.lego.com/en-us/stores/stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		country_list = response.xpath('//div[@class="row-block mark-box"]')
		for country in country_list:
				country_name = self.validate(country.xpath('.//div[@class="heading"]//h3/text()').extract_first())
				store_list = country.xpath('.//ul[@class="city-list"]//li')
				for store in store_list:
					try:
						item = ChainItem()
						detail = self.eliminate_space(store.xpath('.//address//text()').extract())
						item['store_name'] = self.validate(store.xpath('.//h6/text()').extract_first())
						item['address'] = detail[0]
						if country_name  == 'USA':
							address = detail[0] + ', ' + detail[1]
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
						elif country_name == 'Canada':
							addr = detail[1].split(' ')
							item['zip_code'] = addr[-1] + ' ' + addr[-2]
							item['state'] = addr[-3]
							item['city'] = ''
							for ad in addr[:-3]:
								item['city'] += self.validate(ad) + ' '
						elif country_name == 'Austria' or country_name == 'Belgium':
							item['city'] = self.validate(detail[1].split(' ')[1])
							item['zip_code'] = self.validate(detail[1].split(' ')[0])
						elif country_name == 'Sweden':
							item['city'] = self.validate(detail[1].split(' ')[2])
							item['zip_code'] = self.validate(detail[1].split(' ')[0]) + self.validate(detail[1].split(' ')[1])
						elif country_name == 'United Kingdom':
							addr = detail[1].split(' ')
							if len(detail) == 2:
								addr = detail[0].split(' ')
								item['address'] = ''
								item['phone_number'] = self.validate(detail[1].split('Phone:')[1])
							item['zip_code'] = ''
							item['city'] = ''
							for ad in addr[:2]:
								item['zip_code'] += self.validate(ad) + ' '
							for ad in addr[2:]:
								item['city'] += self.validate(ad) + ' '
						else:
							item['city'] = self.validate(detail[1].split(' ')[0])
							item['zip_code'] = self.validate(detail[1].split(' ')[1])
							if len(detail) == 2:
								item['address'] = ''
								item['city'] = self.validate(detail[0].split(' ')[0])
								item['zip_code'] = self.validate(detail[0].split(' ')[1])
								item['phone_number'] = self.validate(detail[1].split('Phone:')[1])
						item['country'] = country_name
						try:
							item['phone_number'] = self.validate(detail[2].split('Phone:')[1])
						except:
							pass
						h_temp = ''
						hour_list = self.eliminate_space(store.xpath('.//div[@class="hours-list"]//text()').extract())
						for hour in hour_list:
							h_temp += hour + ', '
						item['store_hours'] = h_temp[:-2]
						yield item	
					except:
						pass

	def validate(self, item):
		try:
			return item.strip().replace('\n','').replace('\r','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp