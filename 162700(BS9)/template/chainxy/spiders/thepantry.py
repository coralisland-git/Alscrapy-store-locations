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

class thepantry(scrapy.Spider):
	name = 'thepantry'
	domain = 'http://www.mystore411.com'
	history = []
	count = 0

	def start_requests(self):
		init_url = 'http://find.mapmuse.com/brand/kangaroo-express'
		yield scrapy.Request(url=init_url, callback=self.parse_state)	

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="col-md-4"]//table//tr//td[1]//a[@title="Kangaroo Express"]/@href').extract()
		for state in state_list:	
			yield scrapy.Request(url=state, callback=self.parse_city)

	def parse_city(self, response):
		city_list = response.xpath('//div[@class="col-md-4"]//table//tr//td[1]//a[@title="Kangaroo Express"]/@href').extract()
		for city in city_list:
			temp = city.split('/')
			state = temp[len(temp)-2]
			city = temp[len(temp)-1]
			url = 'http://find.mapmuse.com/resp/topic_minimap_city.php?b=kangaroo-express&sta=%s&cit=%s' %(state, city)
			yield scrapy.Request(url=url, callback=self.parse_store)

	def parse_store(self, response):
		try:
			store_list = response.xpath('//div[@class="panel panel-info"]')
			for store in store_list:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//div[@class="panel-body"]//text()').extract())
				n_temp = self.eliminate_space(store.xpath('.//h3//a/text()').extract_first().split('-'))
				item['store_name'] = self.validate(n_temp[0])
				address0 = ''
				for cnt in range(1, len(n_temp)) :
					address0 += n_temp[cnt].replace('.','') + ' '
				address = self.validate(address0) + ', ' + detail[0]
				if '(' in address:
					address = self.validate(address.split('(')[0])
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
				item['country'] = 'United States'
				item['phone_number'] = ''
				try:
					item['phone_number'] = detail[1]
				except:
					pass
				if item['address']+item['phone_number'] not in self.history:
					self.history.append(item['address']+item['phone_number'])
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