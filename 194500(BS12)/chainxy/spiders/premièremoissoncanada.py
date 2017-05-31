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

class premieremoissoncanada(scrapy.Spider):
	name = 'premieremoissoncanada'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://premieremoisson.com/en/branches'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "branch-item")]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			store = response.xpath('//section[@class="succursale-list succursale-single clearfix"]//div[contains(@class, "box-wrap")]//div[@class="box"]')
			detail = self.eliminate_space(store[0].xpath('.//text()').extract())
			item['store_name'] = detail[0]
			addr = self.eliminate_space1(detail[1].split(','))
			if len(addr) == 2:
				if '(' in addr[1]:
					item['address'] = addr[0]
					item['city'] = addr[1].split('(')[0].strip()
					item['state'] = addr[1].split('(')[1].split(')')[0].strip()
					item['zip_code'] = addr[1].split(')')[1].strip()
				else:
					a_list = addr[0].split(' ')
					item['address'] = ''
					for temp in a_list[:-1]:
						item['address'] += temp + ' '
					item['city'] = self.validate(a_list[-1])
					sz_list = addr[1].strip().split(' ')
					s_temp = ''
					for temp in sz_list[:-2]:
						s_temp += temp + ' '
					item['state'] = self.validate(s_temp)
					z_temp = ''
					for temp in sz_list[-2:]:
						z_temp += temp + ' '
					item['zip_code'] = self.validate(z_temp)
			elif len(addr) == 5 or len(addr) == 4:
				item['address'] = addr[0]
				item['city'] = self.validate(addr[1])
				item['state'] = self.validate(addr[2])
				item['zip_code'] = self.validate(addr[3])
			else:
				item['address'] = addr[0]
				item['city'] = addr[1]
				# a_list = addr[0].split(' ')
				# item['address'] = ''
				# for temp in a_list[:-1]:
				# 	item['address'] += temp + ' '
				# item['city'] = self.validate(a_list[-1])
				if item['address'] == '790':
					item['address'] = addr[0]
					a_list = addr[1].split(' ')
					item['address'] = ''
					for temp in a_list[:-1]:
						item['address'] += temp + ' '
					item['city'] = self.validate(a_list[-1])
				sz_list = addr[2].strip().split(' ')
				s_temp = ''
				for temp in sz_list[:-2]:
					s_temp += temp + ' '
				item['state'] = self.validate(s_temp)
				z_temp = ''
				for temp in sz_list[-2:]:
					z_temp += temp + ' '
				item['zip_code'] = self.validate(z_temp)
			item['country'] = 'Canada'
			item['phone_number'] = detail[2]
			h_temp = ''
			hour_list = self.eliminate_space(store[1].xpath('.//text()').extract())
			cnt = 1
			for hour in hour_list:
				h_temp += hour
				if cnt % 2 == 0:
					h_temp += ', '
				else:
					h_temp += ' '
				cnt += 1
			item['store_hours'] = h_temp[:-2]
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
			if self.validate(item) != '' and 'hours' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def eliminate_space1(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'canada' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp