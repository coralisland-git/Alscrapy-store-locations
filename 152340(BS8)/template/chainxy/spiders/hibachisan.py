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

class hibachisan(scrapy.Spider):
	name = 'hibachisan'
	domain = 'http://www.hibachisan.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.hibachisan.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		state_list = response.xpath('//select//option/@value').extract()
		for state in state_list:
			state = 'http://www.hibachisan.com/locations/locatorresults.aspx?state=%s' % state
			yield scrapy.Request(url=state, callback=self.parse_store)

	def parse_store(self, response):
		try:
			store_list = response.xpath('//table[@id="ctl00_ContentPlaceHolder1_dlGetStoresByState"]/tr')
			for cnt in range(0, len(store_list)):
				detail = self.eliminate_space(store_list[cnt].xpath('.//table//tr[1]//td[1]//text()').extract())
				item = ChainItem()
				address = ''
				num = 0
				for ind in range(0, len(detail)-1):
					if 'Phone:' in detail[ind]:
						item['phone_number'] = self.validate(detail[ind].split(':')[1])	
						num = ind
				if num == 5:					
					item['store_name'] = self.validate(detail[0])
					item['address'] = self.validate(detail[1])			
					item['city'] = self.validate(detail[2])
					item['state'] = self.validate(detail[3])
					item['zip_code'] = self.validate(detail[4])
				elif num == 6:
					item['store_name'] = self.validate(detail[0]) + self.validate(detail[1])
					item['address'] = self.validate(detail[2])			
					item['city'] = self.validate(detail[3])
					item['state'] = self.validate(detail[4])
					item['zip_code'] = self.validate(detail[5])
				item['country'] = 'United States'
				h_temp = '  '
				try:
					hour_list_name = store_list[cnt].xpath('.//table//tr[2]//table//tr[1]//th/text()').extract()
					hour_list_open = store_list[cnt].xpath('.//table//tr[2]//table//tr[2]//td/text()').extract()
					hour_list_close = store_list[cnt].xpath('.//table//tr[2]//table//tr[3]//td/text()').extract()
					for cnt in range(0, len(hour_list_name)):
						h_temp += hour_list_name[cnt] + ' ' + hour_list_open[cnt] + '-' + hour_list_close[cnt] + ', '
				except:
					pass
				item['store_hours'] = self.validate(h_temp[:-2])	
				yield item

			pagenation = response.xpath('//a[@id="ctl00_ContentPlaceHolder1_btnNext"]/@href').extract_first()
			if pagenation is not None:
				pagenation = self.domain + pagenation
				yield scrapy.Request(url=pagenation, callback=self.parse_store)
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and self.validate(item) != ',':
				tmp.append(self.validate(item))
		return tmp
