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

class gigiscupcakes(scrapy.Spider):
	name = 'gigiscupcakes'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://gigiscupcakesusa.com/locations/'

		header = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="textwidget"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="post-title entry-title"]//a/text()').extract_first())
			detail = self.eliminate_space(response.xpath('//div[@class="flex_column av_one_half  flex_column_div   "][1]//text()').extract())
			address = ''
			for de in detail:
				che = de.split('-')
				if len(che) == 3 or '(' in de or 'open' in de.lower() or 'located' in de.lower() or ':' in de:
					break
				address += de + ', '
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(address[:-2])
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
			for de in detail:
				if ':' in de or '|' in de:
					item['store_hours'] = de
				elif '-' in de:
					item['phone_number'] = de
			if item['store_name'] != '':
				yield item
		except:
			pass

	def validate(self, item):
		try:
			return item.encode('raw-unicode-escape').replace('\u2013', '-').replace('\xa0',' ').replace('\\n', '').replace('&#8211;', '-').replace('&#038;', '-').replace('\n','').replace('&#8217;','').strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'mother' not in self.validate(item).lower() and 'contact' not in self.validate(item).lower() and 'village' not in self.validate(item).lower():
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'