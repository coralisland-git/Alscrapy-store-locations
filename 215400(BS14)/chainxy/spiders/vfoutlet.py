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

class vfoutlet(scrapy.Spider):
	name = 'vfoutlet'
	domain = 'http://www.vfoutlet.com/'
	history = []

	def start_requests(self):
		init_url = 'http://www.vfoutlet.com/storelocator/index/loadstore/'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for cnt in range(1, 5):
			formdata = {
				"tagIds":"",
				"curPage":str(cnt)
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['storesjson']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['store_name'])
				item['address'] = self.validate(store['address_2'])
				if len(store['address_2']) < 12:
					item['address'] = self.validate(store['address']) + ' '+ self.validate(store['address_2'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['latitude'])
				item['longitude'] = self.validate(store['longitude'])
				url = self.domain + self.validate(store['rewrite_request_path'])
				yield scrapy.Request(url=url, callback=self.parse_page, meta={'item':item})
			except:
				pass

	def parse_page(self, response):
		try:
			item = response.meta['item']
			detail = response.xpath('//div[contains(@class, "box-detail")]//p[@class="col-full"]')
			item['city'] = self.eliminate_space(detail[1].xpath('.//text()').extract())[1]
			item['state'] = self.eliminate_space(detail[2].xpath('.//text()').extract())[1]
			item['country'] = self.eliminate_space(detail[3].xpath('.//text()').extract())[1]
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@id="open_hour"]//table//text()').extract())
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
		for state in self.US_CA_States_list:
			if item in state['name']:
				return state['country']
		return ''