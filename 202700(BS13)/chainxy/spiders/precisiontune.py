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

class precisiontune(scrapy.Spider):
	name = 'precisiontune'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.precisiontune.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('var PTFranchiseeLocations = ')[1].strip().split('</script>')[0][:-12]
		store_list = json.loads(data)
		for store in store_list:
			url = store['data']['url']
			request = scrapy.Request(url=url, callback=self.parse_page, meta={
				'latitude':store['position']['lat'],
				'longitude':store['position']['lng']
				})
			yield request

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.str_concat(response.xpath('//h1[@itemprop="name"]//text()').extract(), ' ')
			detail = self.eliminate_space(response.xpath('//div[@id="content"]/p//text()').extract())
			item['store_number'] = detail[0].split(' ')[2]
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(detail[1])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0].replace(',','')
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail[2].split('Phone:')[1])
			item['latitude'] = response.meta['latitude']
			item['longitude'] = response.meta['longitude']
			h_temp = ''
			hour_list = self.eliminate_space(response.xpath('//div[@class="sidenavs"]//div[@class="columnize"][2]//text()').extract())
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