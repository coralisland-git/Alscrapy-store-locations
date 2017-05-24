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

class hsbcbankusa(scrapy.Spider):
	name = 'hsbcbankusa'
	domain = 'https://www.banking.us.hsbc.com'
	history = []
	count = 0

	def start_requests(self):
		init_url = 'https://www.banking.us.hsbc.com/HICServlet?cmd_GetUSMap='
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		state_list = response.xpath('//map[@name="m_US_MAP_mr"]//area/@href').extract()
		for state in state_list:
			state = self.domain + state
			yield scrapy.Request(url=state, callback=self.parse_store)

	def parse_store(self, response):
		try:
			store_list = self.eliminate_space(response.xpath('//table//table//tr[@valign="top"]//a/@href').extract())
			for store in store_list:
				store = self.domain + store
				yield scrapy.Request(url=store, callback=self.parse_page)
		except:
			pass
		try:
			yield scrapy.Request(url=response.url, callback=self.parse_page)
		except:
			pass

	def parse_page(self, response):
		store_list = response.xpath('//table[@width="525"]')
		if len(store_list) == 0:
			store_list = response.xpath('//table[@class="table_width525"]')
		for store in store_list:
			try:
				item = ChainItem()
				detail = self.eliminate_space(store.xpath('.//tr[1]/td[1]/text()').extract())
				item['store_name'] = self.eliminate_space(store.xpath('.//tr[1]//td[1]//strong//text()').extract())[0]
				address = ''
				for de in detail:
					address += de + ', '
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
				h_temp = ''
				h_temp += 'Lobby : '
				hour_list = store.xpath('.//tr[1]//td[2]//table//tr')
				for cnt in range(1, len(hour_list)):
					h_temp += self.validate(hour_list[cnt].xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour_list[cnt].xpath('.//td[2]/text()').extract_first()) + ', '
				h_temp += ' Drive_Thru : '
				for cnt in range(1, len(hour_list)):
					if self.validate(hour_list[cnt].xpath('.//td[3]/text()').extract_first()) != '':
						h_temp += self.validate(hour_list[cnt].xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour_list[cnt].xpath('.//td[3]/text()').extract_first()) + ', '

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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''