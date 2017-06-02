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

class federatedcc(scrapy.Spider):
	name = 'federatedcc'
	domain = 'http://www.federatedcc.com/'
	location_list = []
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			zipcode = str(location['zipcode'])
			count = len(zipcode)
			count = 5 - count
			i = 0
			while i < count:
				zipcode = '0' + zipcode
				i += 1
			init_url = 'http://www.federatedcc.com/shopresults.aspx?cname=SearchResult&zip=%s&city=&state=&m=10' % (zipcode)
			# yield scrapy.Request(url=init_url, callback=self.body) 
			yield scrapy.Request(url='http://www.federatedcc.com/shopresults.aspx?cname=SearchResult&zip=99206&city=&state=&m=10', callback=self.body)

	def body(self, response):
		store_list = self.eliminate_space(response.xpath('//div[@class="STOREINFO"]//table//tr//td[@nowrap="nowrap"]//a/@href').extract())
		if store_list:
			for store in store_list:
				try:
					link_list = store.split('/')
					count = len(link_list)
					store_number = link_list[count - 2]
					if store_number not in self.history:
						self.history.append(store_number)
						request = scrapy.Request(url=store, callback=self.parse_page)
						request.meta['store_number'] = store_number
						yield request
				except:
					pass

	def parse_page(self, response):
		store = response.xpath('//table[@id="LocationDetailTable"]//table//table//table')
		try:
			try:
				store = store[0]
				link = self.validate(store.xpath('.//tr')[10].xpath('.//td//a')[0].xpath('./@href').extract_first())
				item = ChainItem()
				item['store_number'] = response.meta['store_number']
				item['store_name'] = self.validate(store.xpath('.//tr')[0].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['address'] = self.validate(store.xpath('.//tr')[1].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['city'] = self.validate(store.xpath('.//tr')[2].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['state'] = self.validate(store.xpath('.//tr')[3].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['country'] = self.validate(store.xpath('.//tr')[4].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['zip_code'] = self.validate(store.xpath('.//tr')[5].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['phone_number'] = self.validate(store.xpath('.//tr')[6].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['longitude'] = self.validate(store.xpath('.//tr')[8].xpath('.//td//p')[1].xpath('./text()').extract_first())
				item['latitude'] = self.validate(store.xpath('.//tr')[9].xpath('.//td//p')[1].xpath('./text()').extract_first())
			except:
				pass
			if link:
				link = self.domain + link
				request = scrapy.Request(url=link, callback=self.parse_detail, meta={'data':item})
				yield request
			else:
				yield item
		except:
			pass

	def parse_detail(self, response):
		item = ChainItem()
		item = response.meta['data']
		hour_list = self.eliminate_space(response.xpath('//div[@id="maincontent-left"]//div[@id="banner-back"]')[1].xpath('.//p//text()').extract())
		h_temp = ''
		cnt = 1
		for hour in hour_list:
			h_temp += hour
			if cnt % 2 == 0:
				h_temp += ', '
			else:
				h_temp += ' '
			cnt += 1
		item['store_hours'] = self.format(h_temp[:-2])
		yield item

	def format(self, item):
		try:
			return item.encode('raw-unicode-escape').strip()
		except:
			return ''

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