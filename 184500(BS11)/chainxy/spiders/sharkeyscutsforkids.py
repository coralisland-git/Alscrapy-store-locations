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

class sharkeyscutsforkids(scrapy.Spider):
	name = 'sharkeyscutsforkids'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://sharkeyscutsforkids.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//p[@class="store-p"]')
		for store in store_list:
			status = store.xpath('.//span[@class="store-sub-title"]/text()').extract_first()
			detail = store.xpath('.//a/text()').extract_first()
			if '-' in detail:
				detail = detail.split('-')
			else:
				detail = detail.split(',')
			if status:
				if 'coming' in status.lower() or 'opening' in status.lower():
					item = ChainItem()
					item['city'] = self.validate(detail[0])
					item['state'] = self.validate(detail[1])
					item['country'] = 'United States'
					if item['state'] == 'Canada':
						item['country'] = 'Canada'
						item['state'] = ''
					item['coming_soon'] = '1'

					yield item
			else:
				country = 'United States'
				if 'UK' in detail[1]  or 'Isle of Man' in detail[1]:
					country = 'United Kingdom'
				elif 'Manitoba' in detail[1] or 'Ontario' in detail[1]:
					country = 'Canada'					
				yield scrapy.Request(url=store.xpath('.//a/@href').extract_first(), callback=self.parse_page, meta={'country':country})

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "hair-sidebar")]/div[@class="row"][1]//p/text()').extract())
			if response.meta['country'] == 'United Kingdom':
				detail = self.eliminate_space(response.xpath('//div[contains(@class, "hair-sidebar")]/div[@class="row"][1]//text()').extract())
				if len(detail) == 9:
					item['address'] = detail[1] + ' ' + detail[2]
					item['city'] = detail[3]
					item['state'] = detail[4]
					item['zip_code'] = detail[5]
					item['phone_number'] = detail[6]
				else:
					item['address'] = detail[1]
					item['city'] = detail[2]
					item['state'] = detail[3]
					item['zip_code'] = detail[4]
					item['phone_number'] = detail[5]
			elif response.meta['country'] == 'Canada':
				detail = self.eliminate_space(response.xpath('//div[contains(@class, "hair-sidebar")]/div[@class="row"][1]//text()').extract())
				if len(detail)  < 7:
					item['address'] = detail[0]
					item['city'] = detail[1].split(',')[0]
					item['state'] = detail[1].split(',')[1]
					item['zip_code'] = detail[2]
					item['phone_number'] = detail[3]
				else:
					item['address'] = detail[1]
					item['city'] = detail[3].split(',')[0]
					item['state'] = detail[3].split(',')[1]
					item['zip_code'] = detail[4]
					item['phone_number'] = detail[5]
			else :
				address = ''
				for de in detail:
					if '-' in de and len(de) < 15:
						item['phone_number'] = de
						break
					else :
						address += de + ' '
						if '(' in de:
							address += de.split('(')[0] + ' '
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
			item['country'] = response.meta['country']
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[contains(@class, "hair-sidebar")]/div[@class="row"][2]//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
			item['coming_soon'] = '0'
			yield item	
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
			if self.validate(item) != '' and 'contact' not in self.validate(item).lower() and 'hours' not in self.validate(item).lower() and 'online' not in self.validate(item).lower():
				if '- ' in self.validate(item):
					item = item.replace('- ', '')
				if '(' in self.validate(item) and '+' not in self.validate(item):
					item = self.validate(item.split('(')[0])
				tmp.append(self.validate(item))
		return tmp
